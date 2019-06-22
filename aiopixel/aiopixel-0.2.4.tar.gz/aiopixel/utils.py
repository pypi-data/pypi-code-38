import re

import aiohttp


async def get_player_name(uuid: str, session=None):
    session = aiohttp.ClientSession() if session is None else session
    url = "https://api.mojang.com/user/profiles/{}/names".format(clean_uuid(uuid))

    async with session.get(url) as r:
        data = await r.json()
    return data[-1]["name"]


async def get_player_uuid(name: str, session=None):
    session = aiohttp.ClientSession() if session is None else session
    headers = {
        "Content-Type": "application/json"
    }
    r_data = [name]
    url = "https://api.mojang.com/profiles/minecraft"
    async with session.post(url, json=r_data, headers=headers) as r:
        data = await r.json()
    if data:
        return data[0]["id"]
    else:
        return None


def clean_uuid(uuid: str) -> str:
    return re.sub("-", "", uuid)
