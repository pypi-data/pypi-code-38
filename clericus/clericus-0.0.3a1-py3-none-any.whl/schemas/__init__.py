import asyncio

from .user import createUserCollection
from .authentication import createAuthenticationCollection
from .activity import createActivityCollection


async def createCollections(db):
    await asyncio.wait([
        createUserCollection(db),
        createAuthenticationCollection(db),
        createActivityCollection(db)
    ])