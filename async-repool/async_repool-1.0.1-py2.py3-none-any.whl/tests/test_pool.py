import asyncio
import asynctest


class ConnectionMock:

    def is_open(self):
        return True

    async def close(self, noreply_wait=True):
        pass


class TestPool(asynctest.TestCase):

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_create_pool(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict())
        await p.init_pool()
        self.assertFalse(p.empty)
        await p.release_pool()

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_acquire_release_one(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict())
        await p.init_pool()
        nb_init = p._pool.qsize()
        conn = await p.acquire()
        await p.release(conn)
        nb_term = p._pool.qsize()
        self.assertEqual(nb_init, nb_term)
        await p.release_pool()

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_acquire_one(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict())
        await p.init_pool()
        nb_init = p._pool.qsize()
        conn = await p.acquire()
        nb_term = p._pool.qsize()
        self.assertEqual(nb_init - 1, nb_term)
        await p.release(conn)
        await p.release_pool()

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_acquire(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict())
        await p.init_pool()
        conn = await p.acquire()
        self.assertIsInstance(conn, ConnectionMock)
        await p.release(conn)
        await p.release_pool()

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_release_pool(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool, PoolException
        p = AsyncConnectionPool(dict())
        await p.init_pool()
        conn1 = await p.acquire()
        conn2 = await p.acquire()
        await p.release(conn1)
        with self.assertRaises(PoolException):
            await p.release_pool()

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_connect(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict(), pool_size=1)
        await p.init_pool()
        async with p.connect() as conn:
            self.assertEqual(0, p._pool.qsize())
        self.assertEqual(1, p._pool.qsize())
        await p.release_pool()


class TestComplexPool(asynctest.TestCase):

    @asynctest.patch('async_repool.async_pool.R.connect', new_callable=asynctest.CoroutineMock, return_value=ConnectionMock())
    async def test_pool_overlap_with_wait(self, mocked_connect):
        from async_repool.async_pool import AsyncConnectionPool
        p = AsyncConnectionPool(dict(), pool_size=1)
        await p.init_pool()

        async def test_couritine():
            async with p.connect() as conn:
                await asyncio.sleep(1)

        await asyncio.wait([test_couritine() for _ in range(0, 3)])
