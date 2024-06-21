import asyncio
import re
from typing import AsyncIterator

from aiohttp import ClientSession
from cache import AsyncLRU
from cachetools import cached
from config import API_URL

ID_IN_URL = re.compile(r"/[a-z]+/(\d+)/$")  # регулярка вытаскивает id из URL


@cached({})
def get_session():
    #  кеширум получение сесии, таким образом будем использовать одну сессию для всех запросов

    return ClientSession()


async def close_session():
    #  функция для закрытия закешированной сессии

    await get_session().close()


async def get_json(url: str) -> dict:
    session = get_session()
    async with session.get(url) as response:
        return await response.json()


@AsyncLRU(1024)
async def get_json_cached(url: str):
    # для того, чтобы не ходить дваждв по одно ссылке, запросы фильмов, планет, видов транспорта кеширум

    return await get_json(url)


async def prepare_person(person_dict: dict) -> dict:
    """
    :param person_dict: json  с одним персонажем
    :return: словарь персонажа с подготовленными названиями фильмов, планет и т.п
    """

    # создаем задачи на выгрузки фильмов, планет и т.п
    films_tasks = [asyncio.create_task(get_json_cached(url)) for url in person_dict["films"]]
    species_tasks = [asyncio.create_task(get_json_cached(url)) for url in person_dict["species"]]
    starships_tasks = [asyncio.create_task(get_json_cached(url)) for url in person_dict["starships"]]
    vehicles_tasks = [asyncio.create_task(get_json_cached(url)) for url in person_dict["vehicles"]]
    homeworld = asyncio.create_task(get_json_cached(person_dict["homeworld"]))

    #  дожидаемся выгрузки и преобразуем в требуемый формат
    films = await asyncio.gather(*films_tasks)
    films_titles = ",".join(film["title"] for film in films)

    species = await asyncio.gather(*species_tasks)
    species_names = ",".join(specie["name"] for specie in species)

    starships = await asyncio.gather(*starships_tasks)
    starships_names = ",".join(starship["name"] for starship in starships)

    vehicles = await asyncio.gather(*vehicles_tasks)
    vehicles_names = ",".join(vehicles["name"] for vehicles in vehicles)

    homeworld = await homeworld
    homeworld_name = homeworld["name"]

    return {
        "id_person": ID_IN_URL.search(person_dict["url"]).group(1),
        "name": person_dict["name"],
        "birth_year": person_dict["birth_year"],
        "eye_color": person_dict["eye_color"],
        "films": films_titles,
        "gender": person_dict["gender"],
        "hair_color": person_dict["hair_color"],
        "height": person_dict["height"],
        "homeworld": homeworld_name,
        "mass": person_dict["mass"],
        "skin_color": person_dict["skin_color"],
        "species": species_names,
        "starships": starships_names,
        "vehicles": vehicles_names,
    }


async def get_people() -> AsyncIterator[dict]:
    """
    swapi позволяет выгружать данные пачками постранично
    роут /api/people/ вернут json c полями
    results - в котором список персонажей
    next - в котором ссылка на получение следующкй пачки персонажей
    :return:
    """

    next_page_task = asyncio.create_task(get_json(f"{API_URL}/people"))

    while next_page_task:
        response = await next_page_task
        next_page = response["next"]   # станица со слудуюей пачкой персонажей
        if next_page:
            next_page_task = asyncio.create_task(get_json(next_page))
            # сразу начинаем выгружать слудующую страницу, если она есть

        else:
            next_page_task = None
        people = response["results"] # пачка пепсонажей

        # подготавливаем текущую пачку персонажей
        prepare_person_coros = [asyncio.create_task(prepare_person(person)) for person in people]
        prepared_people = await asyncio.gather(*prepare_person_coros)
        for person in prepared_people:
            yield person
