import asyncio

from aioitertools.more_itertools import chunked
from api import close_session, get_people
from config import CHUNK_SIZE
from database import Session, SWapiPeople, close_engine, init_orm


async def put_people_chunk_to_db(people_chunk):
    async with Session() as session:
        session.add_all([SWapiPeople(**person) for person in people_chunk])
        await session.commit()


async def main():
    await init_orm()

    async for people_chunk in chunked(get_people(), CHUNK_SIZE):
        asyncio.create_task(put_people_chunk_to_db(people_chunk))
    await close_session()

    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}
    for task in tasks:
        await task

    await close_engine()


if __name__ == "__main__":
    asyncio.run(main())
