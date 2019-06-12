import os
import asyncio
import logging
import riemann

from zeta import crypto, electrum, utils
from zeta.sync import chain, coins, tx_cache
from zeta.db import connection, headers
# from zeta.db import addresses

from typing import Optional, Tuple
from zeta.zeta_types import Header, Prevout, TransactionEntry


async def _report_best_block() -> None:
    '''
    Logs stats about the heaviest (best) block every 10 seconds
    '''
    best = None
    while True:
        heaviest = headers.find_heaviest()

        # it'd be very strange if this failed
        # but I put in the check, which implies that it happened in testing
        if len(heaviest) != 0:
            if best and heaviest[0]['height'] > best['height']:
                utils.LOGGER.info('chain tip advanced {} block(s)'.format(
                    heaviest[0]['height'] - best['height']
                ))
            best = heaviest[0]
            utils.LOGGER.info('Best Block: {} at {} with {} work'.format(
                best['hash'],
                best['height'],
                best['accumulated_work']
            ))
        await asyncio.sleep(15)


async def _report_new_headers(header_q) -> None:
    # log header hashes as they come in
    def make_block_hash(h) -> str:
        # log the header hash in a human-readable format
        return('new header: {}'.format(
            crypto.hash256(bytes.fromhex(h['hex']))[::-1].hex()))
    asyncio.ensure_future(utils.queue_logger(header_q, make_block_hash))


async def _report_new_prevouts(prevout_q) -> None:
    def humanize_prevout(prevout) -> str:
        if prevout['spent_at'] == -2:
            return('new prevout: {} sat at {} in {}...{}'.format(
                prevout['value'],
                prevout['address'][:12],
                prevout['outpoint']['tx_id'][:8],
                prevout['outpoint']['index']))
        else:
            return('spent prevout: {} sat at {} in {}...{} block {}'.format(
                prevout['value'],
                prevout['address'][:12],
                prevout['outpoint']['tx_id'][:8],
                prevout['outpoint']['index'],
                prevout['spent_at']))
    asyncio.ensure_future(utils.queue_logger(prevout_q, humanize_prevout))


async def _report_new_txns(tx_q: 'asyncio.Queue[TransactionEntry]') -> None:
    def humanize_tx(tx: TransactionEntry) -> str:
        return ('tx store updated: {} at height {} is {}'.format(
            tx['tx_id'],
            tx['confirmed_height'],
            'verified' if tx['merkle_verified'] else 'not verified'))
    asyncio.ensure_future(utils.queue_logger(tx_q, humanize_tx))


async def zeta(
        header_q: Optional['asyncio.Queue[Header]'] = None,
        prevout_q: Optional['asyncio.Queue[Prevout]'] = None,
        tx_q: Optional['asyncio.Queue[TransactionEntry]'] = None,
        network: str = 'bitcoin_main',
        app_name: Optional[str] = None) \
        -> Tuple['asyncio.Future[None]', ...]:
    '''
    Main function.
    Starts the various tasks.
    Pass in queues to access task outputs (new headers/prevout events)
    Returns references to the tasks
    '''
    # switch zeta and riemann over to whatever network we're using
    chain_name = os.environ.get('ZETA_NETWORK', network)
    riemann.select_network(chain_name)

    if app_name is None:
        raise ValueError('must supply a unique application name')

    # start the DB and the electrum connection
    try:
        utils.set_logger(name='zeta.{}'.format(app_name))
    except RuntimeError:
        pass  # allows others to set logger before invoking zeta
    connection.init_conn(chain_name=chain_name, db_name=app_name)

    utils.LOGGER.info('attempting to connect to servers')
    await electrum.electrum._make_client(chain_name)

    # set up the various syncing tasks
    chain_task = asyncio.ensure_future(chain.sync(header_q, chain_name))
    coin_task = asyncio.ensure_future(coins.sync(prevout_q))
    tx_cache_task = asyncio.ensure_future(tx_cache.sync(tx_q))

    return chain_task, coin_task, tx_cache_task


if __name__ == '__main__':
    header_q: 'asyncio.Queue[Header]' = asyncio.Queue()
    prevout_q: 'asyncio.Queue[Prevout]' = asyncio.Queue()
    tx_q: 'asyncio.Queue[TransactionEntry]' = asyncio.Queue()

    chain_name = os.environ.get('ZETA_NETWORK', 'bitcoin_main')
    riemann.select_network(chain_name)

    connection.init_conn(chain_name=chain_name, db_name='terminal')

    logging.basicConfig(
        level='INFO',
        datefmt='%H:%M:%S',
        format='%(asctime)6s %(name)s: %(levelname)s %(message)s')

    # # DEBUG CODE
    # # store a sample address
    # addresses.store_address('tb1qk0mul90y844ekgqpan8mg9lljasd59ny99ata4')

    # start tracking
    zeta_task = zeta(
        header_q=header_q,
        prevout_q=prevout_q,
        tx_q=tx_q,
        network=chain_name,
        app_name='terminal')
    asyncio.ensure_future(zeta_task)

    # start the status updaters
    asyncio.ensure_future(_report_best_block())
    asyncio.ensure_future(_report_new_headers(header_q))
    asyncio.ensure_future(_report_new_prevouts(prevout_q))
    asyncio.ensure_future(_report_new_txns(tx_q))

    # make it go!
    asyncio.get_event_loop().run_forever()
