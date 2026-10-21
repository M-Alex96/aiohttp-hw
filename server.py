from aiohttp import web
import json
from db import init_db, close_db, Session, User, Advertisement
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from auth import hash_password

async def orm_context():
    await init_db()
    yield
    await close_db()

@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app = web.Application()
app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

def get_error(
    err_cls: type[web.HTTPNotFound | web.HTTPConflict | web.HTTPBadRequest],
    err_msg: dict | list | str,
):
    err_msg_json = {
        "error": err_msg,
    }
    return err_cls(
        text=json.dumps(err_msg_json),
        content_type="application/json",
    )

class UserView(web.View):

    @property
    def user_id(self) -> int:
        return int(self.request.match_info["user_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_user(self) -> User:
        user = await self.session.get(User, self.user_id)
        if user is None:
            raise get_error(web.HTTPNotFound, err_msg="User not found")
        return user

    async def add_users(self, user: User) -> None:
        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, err_msg="User already exists")

    async def get(self):
        user = await self.get_user()
        return web.json_response(user.dict)

    async def post(self):
        json_data = await self.request.json()
        if not ("name" in json_data and "password" in json_data):
            raise get_error(web.HTTPBadRequest, err_msg="name and password are required")
        user = User(name = json_data["name"], password=hash_password(json_data["password"]))
        await self.add_users(user)
        return web.json_response(user.id_dict)

    async def patch(self):
        json_data = await self.request.json()
        user = await self.get_user()
        if "name" in json_data:
            user.name = json_data["name"]
        if "password" in json_data:
            user.password = json_data["password"]
        await self.add_users(user)
        return web.json_response(user.id_dict)

    async def delete(self):
        user = await self.get_user()
        await self.session.delete(user)
        await self.session.commit()
        return web.json_response({"status": "deleted"})

class AdvertisementView(web.View):

    @property
    def adv_id(self) -> int:
        return int(self.request.match_info["adv_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get_adv(self) -> Advertisement:
        adv = await self.session.get(Advertisement, self.adv_id)
        if adv is None:
            raise get_error(web.HTTPNotFound, err_msg="Advertisement not found")
        return adv

    async def add_adv(self, adv: Advertisement) -> None:
        self.session.add(adv)
        try:
            await self.session.commit()
        except IntegrityError:
            raise get_error(web.HTTPConflict, err_msg="Advertisement already exists")

    async def get(self):
        adv = await self.get_adv()
        return web.json_response(adv.dict)

    async def post(self):
        json_data = await self.request.json()
        if not ("title" in json_data and "description" in json_data and "owner_id" in json_data):
            raise get_error(web.HTTPBadRequest, err_msg="title, description and owner id are required")
        adv = Advertisement(title = json_data["title"], description = json_data["description"], owner_id = json_data["owner_id"])
        await self.add_adv(adv)
        return web.json_response(adv.id_dict)

    async def patch(self):
        json_data = await self.request.json()
        adv = await self.get_adv()
        if "title" in json_data:
            adv.title = json_data["title"]
        if "description" in json_data:
            adv.description = json_data["description"]
        if "owner_id" in json_data:
            adv.owner_id = json_data["owner_id"]
        await self.add_adv(adv)
        return web.json_response(adv.id_dict)

    async def delete(self):
        adv = await self.get_adv()
        await self.session.delete(adv)
        await self.session.commit()
        return web.json_response({"status": "deleted"})

app.add_routes(
    [
        web.post("/users", UserView),
        web.post("/advertisements", AdvertisementView),
        web.get(r"/users/{user_id:\d+}", UserView),
        web.get(r"/advertisements/{adv_id:\d+}", AdvertisementView),
        web.patch(r"/users/{user_id:\d+}", UserView),
        web.patch(r"/advertisements/{adv_id:\d+}", AdvertisementView),
        web.delete(r"/users/{user_id:\d+}", UserView),
        web.delete(r"/advertisements/{adv_id:\d+}", AdvertisementView),
    ]
)

if __name__ == "__main__":
    web.run_app(app)