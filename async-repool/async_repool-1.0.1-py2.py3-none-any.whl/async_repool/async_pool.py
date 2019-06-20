from asyncio import Queue, Lock
import logging
from typing import Dict, Union, Optional
import time

import rethinkdb
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['AsyncConnectionPool', 'PoolException', 'R']

_log = logging.getLogger(__name__)
R = rethinkdb.RethinkDB()
R.set_loop_type('asyncio')
RETRY_ATTEMPTS = 20


class PoolException(Exception):
    pass


class AsyncConnectionWrapper:

    def __init__(self, pool: 'AsyncConnectionPool', conn=None, **kwargs) -> None:
        self._pool = pool
        self._conn = conn
        self._connection_kwargs = kwargs
        if conn is not None:
            self.connected_at: Optional[float] = time.time()
        else:
            self.connected_at: Optional[float] = None

    async def init_wrapper(self) -> None:
        if self._conn is None:
            self._conn = await R.connect(**self._connection_kwargs)
        self.connected_at = time.time()

    @property
    def expire(self) -> bool:
        if not self._pool.connection_ttl:
            return False
        now = time.time()
        return (now - self.connected_at) > self._pool.connection_ttl  # type: ignore

    @property
    def open(self) -> bool:
        return self._conn.is_open()

    @property
    def connection(self):
        return self._conn


class AsyncConnectionContextManager:  # pylint: disable=too-few-public-methods

    __slots__ = ('pool', 'looped_mode', 'conn')

    def __init__(self, pool: 'AsyncConnectionPool', looped_mode: bool = False) -> None:
        self.pool: 'AsyncConnectionPool' = pool
        self.conn = None
        self.looped_mode = looped_mode

    async def __aenter__(self):
        self.conn = await self.pool.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            if self.looped_mode:
                await self.pool.release_to_looped(self.conn)
            else:
                await self.pool.release(self.conn)


class AsyncConnectionPool:

    __slots__ = (
        'pool_size', 'connection_ttl', '_current_acquired',
        'connection_kwargs', '_pool', '_looped_pool', '_pool_lock'
    )

    def __init__(
            self, rethinkdb_connection_kwargs: Dict[str, Union[str, int]],
            pool_size: int = 10, connection_ttl: int = 3600) -> None:
        self.pool_size = pool_size
        self.connection_ttl = connection_ttl
        self.connection_kwargs = rethinkdb_connection_kwargs
        self._pool: Queue = Queue()
        self._looped_pool: Queue = Queue()
        self._pool_lock = Lock()
        self._current_acquired = 0

    async def init_pool(self) -> None:
        for _ in range(0, self.pool_size):
            await self._pool.put(await self.new_conn())

    async def new_conn(self) -> AsyncConnectionWrapper:
        """
        Create a new AsyncConnectionWrapper instance
        """
        _log.debug("Opening new connection to rethinkdb with args=%s", self.connection_kwargs)
        connection_wrapper = AsyncConnectionWrapper(self, **self.connection_kwargs)
        await connection_wrapper.init_wrapper()
        return connection_wrapper

    @retry(wait=wait_exponential(multiplier=0.3, max=10), retry=retry_if_exception_type(PoolException), stop=stop_after_attempt(RETRY_ATTEMPTS))
    async def acquire(self):
        """
        Acquire a connection
        :returns: Returns a RethinkDB connection
        :raises Empty: No resources are available before timeout.
        """
        if self._current_acquired == self.pool_size:
            raise PoolException("Connection pool is full, please, increase pool size")
        await self._pool_lock.acquire()
        _log.debug('Try to acquire, still acquired %d, pool size %d', self._current_acquired, self.pool_size)
        conn_wrapper = await self._pool.get()
        if not conn_wrapper.open:
            conn_wrapper = await self.new_conn()
        if conn_wrapper.expire:
            _log.debug('Recreate connection due to ttl expire')
            await conn_wrapper.connection.close()
            conn_wrapper = await self.new_conn()
        self._current_acquired += 1
        self._pool_lock.release()
        return conn_wrapper.connection

    async def release(self, conn) -> None:
        """
        Release a previously acquired connection.
        The connection is put back into the pool.
        """
        await self._pool_lock.acquire()
        await self._pool.put(AsyncConnectionWrapper(self, conn))
        self._current_acquired -= 1
        _log.debug('Free connection, still acquired %d, pool size %d', self._current_acquired, self.pool_size)
        self._pool_lock.release()

    async def release_to_looped(self, conn) -> None:
        """
        Release a previously acquired connection.
        The connection is put into the looped pool.
        """
        await self._pool_lock.acquire()
        await self._looped_pool.put(AsyncConnectionWrapper(self, conn))
        self._current_acquired -= 1
        _log.debug('Free connection, still acquired %d, pool size %d', self._current_acquired, self.pool_size)
        self._pool_lock.release()

    @property
    def empty(self) -> bool:
        return self._pool.empty()

    async def release_pool(self) -> None:
        """Release pool and all its connection"""
        if self._current_acquired > 0:
            raise PoolException("Can't release pool: %d connection(s) still acquired" % self._current_acquired)
        await self._pool_lock.acquire()
        for target_pool in (self._pool, self._looped_pool):
            while not target_pool.empty():
                conn = await target_pool.get()
                await conn.connection.close(noreply_wait=False)
        self._pool_lock.release()

    def connect(self, looped_mode: bool = False) -> AsyncConnectionContextManager:
        '''Acquire a new connection with `with` statement and auto release the connection after
            go out the with block
        :param timeout: @see #aquire
        :returns: Returns a RethinkDB connection
        :raises Empty: No resources are available before timeout.
        '''
        return AsyncConnectionContextManager(self, looped_mode=looped_mode)
