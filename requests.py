import asyncio

import aiohttp

from models import Person


async def get_person(person_id: int, http_session: aiohttp.ClientSession) \
        -> dict | None:
    """Получаем из API предподготовленные данные под ORM-модель"""
    response_json = await get_raw_person(person_id, http_session)
    if not response_json:
        return
    model_fields = _get_fields_for_model(response_json)
    for key, value in model_fields.items():
        if isinstance(value, list):
            names = await _get_names(value)
            model_fields[key] = names
    return model_fields


async def get_raw_person(person_id: int, http_session: aiohttp.ClientSession) \
        -> dict | None:
    """Получаем от API по конкретному персонажу
    всю информацию о нем в виде JSON"""
    response = await http_session.get(
        f"https://swapi.dev/api/people/{person_id}")
    if response.status != 200:
        return
    response_json = await response.json()
    return response_json


def _get_fields_for_model(response_json: dict) -> dict:
    """Удаляем из JSON поля, которые отсутствуют в ORM-модели"""
    response_json_copy = response_json.copy()
    for el in response_json:
        if el not in Person.__dict__.keys():
            response_json_copy.pop(el)
    return response_json_copy


def _check_value_in_list(value: list[str]):
    """Проверяем на корректность данные элементов списка"""
    if not isinstance(value, list):
        raise TypeError("Value is not a list type")
    elif not all(isinstance(el, str) for el in value):
        raise TypeError("All or some of value data elements "
                        "are not a str type")
    elif not all(el.startswith("https://") for el in value):
        raise ValueError("All or some of value data elements "
                         "are not URL addresses")


async def _get_names(value: list[str]) -> str:
    """Преобразовываем элементы списка в строку,
    отправляя API-запрос на данный элемент списка"""
    _check_value_in_list(value)
    res_str = ""
    tasks = []
    async with aiohttp.ClientSession() as http_session:
        for el in value:
            coro = http_session.get(el)
            task = asyncio.create_task(coro)
            tasks.append(task)
        res_list = await asyncio.gather(*tasks)
        for el in res_list:
            el = await el.json()
            if el.get("name"):
                el = el["name"]
            elif el.get("title"):
                el = el["title"]
            res_str += el + ", "
        res_str = res_str.rstrip(", ")
        return res_str
