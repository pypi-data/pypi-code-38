import asyncio


async def test_install(guillotina_authentication_requester):  # noqa
    async with guillotina_authentication_requester as requester:
        response, _ = await requester('GET', '/db/guillotina/@addons')
        assert 'guillotina_authentication' in response['installed']
