import aiohttp
import asyncio
import json


class NoKey(Exception):
    pass


class client:
    """Client that handles requests to https://some-random-api.ml"""

    def __init__(self):
        self.base_url = 'https://some-random-api.ml/'
        self.cs = aiohttp.ClientSession

    async def get(self, endpoint, **params):
        """Sends the requests.
        All requests come back as json."""
        async with self.cs() as cs:
            if not params:
                async with cs.get(f'{self.base_url}/{endpoint}/') as r:
                    return await r.json()
            else:
                params = ''.join([f'{key}={params[key]}&' for key in params.keys()])
                async with cs.get(f'{self.base_url}/{endpoint}/?{params}') as r:
                    return await r.json()

    async def meme(self):
        """Gives a meme with image and text."""
        return await self.get('meme')

    async def dog_fact(self):
        """Gives a dog fact."""
        return await self.get('dogfact')

    async def cat_fact(self):
        """Gives a cat fact."""
        return await self.get('catfact')

    async def panda_fact(self):
        """Gives a panda fact."""
        return await self.get('pandafact')

    async def dog(self):
        """Gives a dog image."""
        return await self.get('dogimg')

    async def cat(self):
        """Gives a cat image."""
        return await self.get('catimg')

    async def panda(self):
        """Returns a panda image."""
        return await self.get('pandaimg')

    async def red_panda(self):
        """Return a panda image."""
        return await self.get('redpandaimg')

    async def birb(self):
        """Returns a bird image."""
        return await self.get('birbimg')

    async def fox(self):
        """Return fox image."""
        return await self.get('foximg')

    async def pikachu(self):
        """Returns pikachu image."""
        return await self.get('pikachuimg')

    async def chat(self, text: str):
        """Chats to a bot."""
        return await self.get('chatbot', message=text)

    async def mcname(self, name: str):
        """Shows past names in minecraft."""
        return await self.get('mc', username=name)

    async def bot_token(self):
        """Returns a random bot token."""
        return await self.get('bottoken')

    async def lyrics(self, title: str):
        """Returns lyrics for a song."""
        return await self.get('lyrics', title=title)
