import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        # async with session.get("http://127.0.0.1:8080/users") as resp:
        #     print(resp.status)
        #     print(await resp.text())
        #
        # async with session.get("http://127.0.0.1:8080/advertisements") as resp:
        #     print(resp.status)
        #     print(await resp.text())

        async with session.post(
            "http://127.0.0.1:8080/users",
            json = {"name": "user_1", "password": "1234"}) as resp:
            print(resp.status)
            print(await resp.text())

        async with session.post(
            "http://127.0.0.1:8080/advertisements",
            json = {"title": "Ищу работу", "description": "ИИ забрал мою работу, ищу новую", "owner_id": 1}) as resp:
            print(resp.status)
            print(await resp.text())

        async with session.patch(
            "http://127.0.0.1:8080/users/1",
            json = {"name": "new_name", "password": "1234"}) as resp:
            print(resp.status)
            print(await resp.json())

        async with session.delete(
            "http://127.0.0.1:8080/users/1") as resp:
            print(resp.status)
            print(await resp.json())

        async with session.patch(
            "http://127.0.0.1:8080/advertisements/1",
            json = {"title": "Всё ещё ищу работу", "description": "1234 отклика и всё без результата"}) as resp:
            print(resp.status)
            print(await resp.json())

        async with session.delete(
            "http://127.0.0.1:8080/users/1") as resp:
            print(resp.status)
            print(await resp.json())

        async with session.delete("http://127.0.0.1:8080/advertisements/1") as resp:
            print(resp.status)
            print(await resp.json())


asyncio.run(main())