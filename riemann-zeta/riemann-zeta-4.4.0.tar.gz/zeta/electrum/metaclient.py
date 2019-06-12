import random
import asyncio

from zeta import utils
from zeta.electrum import servers

from connectrum.svr_info import ServerInfo
from connectrum.client import StratumClient
from connectrum import ElectrumErrorResponse

from typing import Any, Awaitable, List, Tuple


class MetaClient():

    def __init__(self):
        self._clients = []
        self._servers = []
        self.protocol_version = "1.2"
        self.user_agent = 'riemann-zeta'

        self._num_clients = 1   # how many servers to connect to
        self._random_set_size = 1  # how many servers to send each RPC
        self._timeout_seconds = 7  # how long to wait for a server response

    async def _keepalive(
            self, c: StratumClient, network: str) -> None:  # pragma: nocover
        '''
        Pings a server every 100 seconds to keep a connection alive
        '''
        while True:
            await asyncio.sleep(100)
            try:
                utils.LOGGER.debug('pinging electrum servers')
                await c.RPC('server.ping')
            except Exception:
                # NB: if it errors, get a new client
                #     and remove from our list of active clients
                utils.LOGGER.debug(
                    'establishing new connection to replace {}'.format(c))
                new_client = await self.new_client(network)
                self._clients.append(new_client)
                self._clients = list(filter(lambda k: k != c, self._clients))
                c = new_client

    async def setup_connections(self, network: str) -> None:
        while len(self._clients) < self._num_clients:
            self._clients.append(await self.new_client(network))

    def _get_server_info(self, network: str) -> ServerInfo:
        '''
        Selects a server randomly from the list
        Filters onions, and other protocol versions

        Returns:
            (ServerInfo): the selected server
        '''
        s = filter(lambda k: k not in self._servers,
                   servers.SERVERS[network])
        s = filter(lambda k: 'onion' not in k['hostname'], s)
        s = filter(lambda k: k['version'] in ['1.2', '1.3', '1.4'], s)
        server = random.choice(list(s))
        return ServerInfo(server)

    async def new_client(self, network: str) -> StratumClient:
        while True:
            server = self._get_server_info(network)
            try:
                client = StratumClient()

                await asyncio.wait_for(
                    client.connect(
                        short_term=True,  # so we can write our own keepalive
                        server_info=server,
                        proto_code='s',
                        use_tor=False,
                        disable_cert_verify=True),
                    timeout=self._timeout_seconds)
                # await client.RPC('server.version', '1.2')
                utils.LOGGER.debug(
                    'established connection to {}'.format(client))
                break

            except Exception:
                # print('failed:', server)
                # print(e, str(e))
                # fall back to top of loop and try a new server
                pass

        asyncio.ensure_future(self._keepalive(client, network))
        self._servers.append(str(server))

        return client

    async def _aggregate_results(self, coros: List[Awaitable[Any]]) -> Any:
        '''
        Takes an array of awaitables, returns the most common result
        '''
        # gather waits for all coros to finish
        res = await asyncio.gather(*coros, return_exceptions=True)

        # TODO: improve handling here. sometimes we might expect errors
        # filter out electrum error responses
        res = list(filter(lambda k: type(k) is not ElectrumErrorResponse, res))

        utils.LOGGER.debug('received {} electrum responses'.format(len(res)))

        # if we get any response,
        if len(res) != 0:
            # select the most popular one
            res = max(res, key=res.count)
            # if our coros errored, we want to know.
            if issubclass(type(res), Exception):
                utils.LOGGER.error('Server call errored')
                raise res
            else:
                return res
        # if we don't get any response or error, return None
        utils.LOGGER.debug('No server responses received')
        return None

    async def RPC(self, *args: Any) -> Any:
        '''
        Calls an electrum RPC on multiple clients
        '''
        utils.LOGGER.debug('dispatching RPC call to servers: {}'.format(args))

        # choose a random set of our clients and ask their RPC
        client_set = random.choices(self._clients, k=self._random_set_size)
        coros = [c.RPC(*args) for c in client_set]

        # send those coros for aggregation
        return await self._aggregate_results(coros)

    def subscribe(self, *args) -> Tuple[Awaitable, asyncio.Queue]:
        utils.LOGGER.debug('starting subscription: {}'.format(args))

        q: asyncio.Queue = asyncio.Queue()

        client_set = random.choices(self._clients, k=self._random_set_size)
        futs_qs = [c.subscribe(*args) for c in client_set]

        futs = [k[0] for k in futs_qs]
        qs = [k[1] for k in futs_qs]

        fut = self._aggregate_results(futs)
        asyncio.ensure_future(self._aggregate_subs(qs, q))

        return fut, q

    async def _aggregate_subs(
            self,
            qs: List[asyncio.Queue],
            outq: asyncio.Queue) -> None:
        '''
        Aggregates events on the subscription queues.
        Keeps a record of the events it has seen, doesn't double send

        Usage note: this should only be used when we generally expect to get
            the same messages around the same time.

        Args:
            qs: the subscription Queues
            outq: events we don't filter will be put here
        '''
        filter_queue: asyncio.Queue = asyncio.Queue()
        seen_once: List[Any] = []

        # this aggregates all the subs to one queue
        for q in qs:
            asyncio.ensure_future(utils.queue_forwarder(q, filter_queue))

        while True:
            # Wait for a message in the queue
            msg = await filter_queue.get()

            if msg in seen_once or self._num_clients == 1:
                await outq.put(msg)
            else:
                seen_once.append(msg)
