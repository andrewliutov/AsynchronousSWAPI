from cachetools import cached
from config import PG_DSN
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


@cached({})
def get_engine():

    return create_async_engine(PG_DSN)


async def close_engine():
    engine = get_engine()
    await engine.dispose()


Session = sessionmaker(bind=get_engine(), class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()


class SWapiPeople(Base):

    __tablename__ = "swapi_people"

    id = Column(Integer, primary_key=True)
    id_person = Column(String)
    birth_year = Column(String)
    eye_color = Column(String)
    films = Column(String)
    gender = Column(String)
    hair_color = Column(String)
    height = Column(String)
    homeworld = Column(String)
    mass = Column(String)
    name = Column(String)
    skin_color = Column(String)
    species = Column(String)
    starships = Column(String)
    vehicles = Column(String)


async def init_orm():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
