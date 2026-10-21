import datetime
import os
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, MappedColumn, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "aiohttp_app")
POSTGRES_HOST= os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT= os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

engine = create_async_engine(POSTGRES_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    name: MappedColumn[str] = mapped_column(String, unique=True)
    password: MappedColumn[str] = mapped_column(String)
    registration_time: MappedColumn[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def id_dict(self):
        return {"id": self.id}
    
    @property
    def dict(self):
        return {"id": self.id, 
                "name": self.name, 
                "registration_time": int(self.registration_time.timestamp())
                }


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    title: MappedColumn[str] = mapped_column(String, nullable=False)
    description: MappedColumn[str] = mapped_column(Text, nullable=False)
    created_at: MappedColumn[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner_id: MappedColumn[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: MappedColumn["User"] = relationship("User")

    @property
    def id_dict(self):
        return {"id": self.id}

    @property
    def dict(self):
        return {"id": self.id,
                "title": self.title,
                "description": self.description,
                "created_at": int(self.created_at.timestamp()),
                "owner": self.owner_id,
                }

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()