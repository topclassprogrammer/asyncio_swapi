import os

from dotenv import load_dotenv
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DSN = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
engine = create_async_engine(DSN)

SessionDB = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(24))
    birth_year: Mapped[str] = mapped_column(String(8))
    gender: Mapped[str] = mapped_column(String(16))
    height: Mapped[str] = mapped_column(String(8))
    mass: Mapped[str] = mapped_column(String(8))
    skin_color: Mapped[str] = mapped_column(String(32))
    hair_color: Mapped[str] = mapped_column(String(32))
    eye_color: Mapped[str] = mapped_column(String(32))
    homeworld: Mapped[str] = mapped_column(String(64))
    films: Mapped[str] = mapped_column(String)
    species: Mapped[str] = mapped_column(String)
    starships: Mapped[str] = mapped_column(String)
    vehicles: Mapped[str] = mapped_column(String)


async def init_orm():
    """Подключаемся к БД и очищаем/создаем таблицы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def insert_people(people_list: list):
    """Записываем ORM-модели в БД"""
    async with SessionDB() as session:
        people_models_list = [
            Person(**person_dict) for person_dict in people_list
        ]
        session.add_all(people_models_list)
        await session.commit()
