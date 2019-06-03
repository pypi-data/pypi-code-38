import helpers
import asyncio


class Test(helpers.AbstractSessionContainer):
    def __init__(self):
        super().__init__(raise_for_status=True)

    @helpers.generator_attach_session
    async def x(self, session=None):
        for i in range(5):
            await asyncio.sleep(0.2)
            yield i

    @helpers.attach_session
    async def y(self, session=None):
        await asyncio.sleep(1)
        return list(range(5))


async def test_asynctools():
    async with Test() as test:
        async for a in test.x():
            print(a)
        for a in await test.y():
            print(a)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_asynctools())
