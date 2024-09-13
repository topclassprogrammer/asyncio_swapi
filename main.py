import asyncio

import aiohttp
import more_itertools

from models import init_orm, insert_people
from requests import get_person

MAX_CHUNK = 5
MAX_PERSONS = 101


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as http_session:
        coros = [get_person(person, http_session)
                 for person in range(1, MAX_PERSONS)]
        tasks = []
        for coros_chunk in more_itertools.chunked(coros, MAX_CHUNK):
            people_list = await asyncio.gather(*coros_chunk)
            people_list_copy = people_list[:]
            # В цикле удаляем из списка элементы со значением None, т.е.
            # те элементы от которых пришел ранее HTTP статус код не равный 200
            for person in people_list:
                if not person:
                    people_list_copy.remove(person)
            task = asyncio.create_task(insert_people(people_list_copy))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
