import asyncio

from riemann import utils as rutils

from zeta.sync import tx_cache
from zeta import electrum, utils
from zeta.db import addresses, headers, prevouts

from typing import Any, cast, List, Optional
from zeta.zeta_types import Header, Outpoint, Prevout, TransactionEntry
from zeta.zeta_types import ElectrumScripthashNotification, \
    ElectrumHistoryTx


async def sync(
        outq: Optional['asyncio.Queue[Prevout]'] = None) \
        -> None:  # pragma: nocover
    '''Starts the syncing tasks'''
    utils.LOGGER.info('starting prevout syncing tasks')
    asyncio.ensure_future(_track_known_addresses(outq))
    asyncio.ensure_future(_maintain_db(outq))


async def _maintain_db(
        outq: Optional['asyncio.Queue[Prevout]'] = None) \
        -> None:  # pragma: nocover
    '''
    Starts any db maintenance tasks we want
    '''
    asyncio.ensure_future(_update_children_in_mempool(outq))
    ...  # TODO: What more here


async def _track_known_addresses(
        outq: Optional['asyncio.Queue[Prevout]']) \
        -> None:  # pragma: nocover
    '''
    Tracks known addresses
    Regularly queries the db to see if we've learned of new addresses
    If we have, spins up a subscription
    '''
    tracked: List[str] = []
    while True:
        # Find the addresses we know
        known_addrs = addresses.find_all_addresses()

        # Figure out which ones we aren't already tracking and track them
        untracked = list(filter(lambda a: a not in tracked, known_addrs))
        # record that we tracked each of them
        for addr in untracked:
            utils.LOGGER.info(
                'tracking new address: {}'.format(addr))
            tracked.append(addr)
            asyncio.ensure_future(_sub_to_address(addr, outq))

        # wait 10 seconds and repeat
        await asyncio.sleep(10)


async def _sub_to_address(
        address: str,
        outq: Optional['asyncio.Queue[Prevout]'] = None) \
        -> None:  # pragma: nocover
    '''
    subs to address and registers a handler
    Args:
        address (str): the address to sub to
        outq  (Queue): the external-facing notification queue
    '''
    # make a new queue for the subscription
    sub_q: asyncio.Queue[ElectrumScripthashNotification] = asyncio.Queue()
    await electrum.subscribe_to_address(address, sub_q)

    # Set up a handler for that queue
    asyncio.ensure_future(_address_sub_handler(address, sub_q, outq))


async def _address_sub_handler(
        address: str,
        inq: 'asyncio.Queue[ElectrumScripthashNotification]',
        outq: Optional['asyncio.Queue[Prevout]']) -> None:  # pragma: nocover
    '''
    Watches an address sub queue, handles events by triggering state checking
    Args:
        address (str): the address we're watching
        inq   (Queue): the subscription queue holding new events
        outq  (Queue): the external-facing notification queue
    '''
    while True:
        # wait for a subscription event
        # it contains no information, so we can discard it
        await inq.get()
        utils.LOGGER.info('got new update for {}'.format(address))
        # update our view of the unspents
        asyncio.ensure_future(_get_address_unspents(address, outq))


async def _get_address_unspents(
        address: str,
        outq: Optional['asyncio.Queue[Prevout]'] = None) \
        -> None:
    '''
    Gets the unspents from an address, and stores them in the DB
    If an out queue is provided, it'll push new prevouts to the queue
    Args:
        address (str): the address we're watching
        outq  (Queue): the external-facing notification queue
    '''
    unspents = await electrum.get_unspents(address)
    utils.LOGGER.debug(
        'electrum server reports {} unspents'.format(len(unspents)))

    electrum_prevout_list = _parse_electrum_unspents(unspents, address)
    elec_outpoints = [p['outpoint'] for p in electrum_prevout_list]

    # see if we know of any
    known_prevouts = prevouts.find_by_address(address)
    known_outpoints = [p['outpoint'] for p in known_prevouts]

    # filter any we already know about
    new_prevouts = list(filter(
        lambda p: p['outpoint'] not in known_outpoints,
        electrum_prevout_list))
    if len(new_prevouts) != 0:
        utils.LOGGER.info('got {} new unspents for address {}'.format(
            len(new_prevouts), address))

    # store new ones in the db and send to the outq if present
    prevouts.batch_store_prevout(new_prevouts)
    if outq is not None:
        for prevout in new_prevouts:
            await outq.put(prevout)

    # check on recently spent prevouts
    _check_recently_spent(
        address=address,
        elec_outpoints=elec_outpoints,
        known_prevouts=known_prevouts,
        outq=outq)


def _check_recently_spent(
        address: str,
        elec_outpoints: List[Outpoint],
        known_prevouts: List[Prevout],
        outq: Optional['asyncio.Queue[Prevout]'] = None) -> None:
    # NB: spent_at is -2 if we think it's unspent
    #     this checks that we think unspent, but electrum thinks spent
    recently_spent = list(filter(
        lambda p: p['spent_at'] == -2 and p['outpoint'] not in elec_outpoints,
        known_prevouts))
    if len(recently_spent) != 0:
        utils.LOGGER.info('got {} new recently spent for address {}'.format(
            len(recently_spent), address))

    # check on those recently spent
    asyncio.ensure_future(_update_recently_spent(
        address=address,
        recently_spent=recently_spent,
        outq=outq))


def _parse_electrum_unspents(
        unspents: List[Any],
        address: str) -> List[Prevout]:
    '''
    Parses Prevouts from the electrum unspent response
    Args:
        unspents (list(dict)): the electrum response
        address         (str): the address associated with the prevout
    Returns:
        (list(Prevout)): the parsed Prevouts
    '''
    prevouts: List[Prevout] = []
    for unspent in unspents:
        prevout: Prevout = {
            'outpoint': {
                'tx_id': unspent['tx_hash'],
                'index': unspent['tx_pos']
            },
            'value': unspent['value'],
            'address': address,
            'spent_at': -2,
            'spent_by': ''
        }
        prevouts.append(prevout)
    return prevouts


async def _update_recently_spent(
        address: str,
        recently_spent: List[Prevout],
        outq: Optional['asyncio.Queue[Prevout]']) -> None:
    '''
    Gets the address history from electrum
    Updates our recently spent
    Args:
        address                  (str): the address we're watching
        recently_spent (list(Prevout)): recently spent prevouts we know of
        outq                   (Queue): the external-facing notification queue
    '''
    # NB: Zeta does NOT use the same height semantics as Electrum
    #     Electrum uses 0 for mempool and -1 for parent unconfirmed
    #     Zeta uses -1 for mempool and -2 for no known spending tx
    if len(recently_spent) == 0:
        return

    history = await electrum.get_history(address)
    utils.LOGGER.debug('server reports {} history items'.format(len(history)))
    # Go through each tx in the history, start with the latest
    for item in history[::-1]:
        asyncio.ensure_future(
            check_history_item_for_spent_prevouts(item, recently_spent, outq))


async def check_history_item_for_spent_prevouts(
        history_item: ElectrumHistoryTx,
        recently_spent: List[Prevout],
        outq: Optional['asyncio.Queue[Prevout]']) -> None:
    '''
    This checks recent history for prevouts we care about that they've spnt
    Args:
        history_item            (dict): the electrum history item dict
        recently_spent (list(Prevout)): recently spent prevouts we know of
        outq                   (Queue): the external-facing notification queue
    '''
    tx_res = await tx_cache.get_tx(history_item['tx_hash'])

    if tx_res is None:
        return
    else:
        historical_tx = cast(TransactionEntry, tx_res)

    # NB: determine which outpoints it spent
    outpoints_spent = [{'tx_id': tx_in.outpoint.tx_id[::-1].hex(),
                        'index': rutils.le2i(tx_in.outpoint.index)}
                       for tx_in in historical_tx['object'].tx_ins]

    # NB: check those against our recently spent prevouts
    recently_spent_by_this_tx = [
        p for p in recently_spent if p['outpoint'] in outpoints_spent]

    utils.LOGGER.info('found {} outpoints spent by {}'.format(
        len(recently_spent_by_this_tx), tx_res['tx_id']))

    # NB: if the TX spent our prevout, get its hash for spent_by
    #     and its block height for spent_at
    for prevout in recently_spent_by_this_tx:
        prevout['spent_by'] = historical_tx['tx_id']
        prevout['spent_at'] = (historical_tx['confirmed_height']
                               if historical_tx['confirmed_height'] > -2
                               else -1)

        # we have assigned a spent_by and height. write it to the db
        prevouts.store_prevout(prevout)
        if outq is not None and prevout['spent_at'] != -2:
            await outq.put(prevout)


async def set_prevout_to_unspent(
        prevout: Prevout,
        outq: Optional['asyncio.Queue[Prevout]'] = None) -> None:
    '''
    Sets a prevout to unspent by removing its spent_by and spent_at
    Args:
        prevout (Prevout): the prevout to set as unsnpent
        outq      (Queue): the external-facing notification queue
    '''
    prevout['spent_at'] = -2
    prevout['spent_by'] = ''
    prevouts.store_prevout(prevout)
    if outq is not None:
        await outq.put(prevout)


async def set_prevout_to_spent(
        prevout: Prevout,
        confirmed_in: str,  # the header hash
        outq: Optional['asyncio.Queue[Prevout]'] = None) -> None:
    '''
    Finds the header that confirmed a tx, and sets the tx to spent
    Args:
        prevout  (Prevout): the prevout to set as snpent
        confirmed_in (str): the hash of the block it was confirmed in
        outq       (Queue): the external-facing notification queue
    '''
    h = headers.find_by_hash(confirmed_in)
    if h is not None:
        confirming = cast(Header, h)
        prevout['spent_at'] = confirming['height']
        prevouts.store_prevout(prevout)
        if outq is not None:
            await outq.put(prevout)


async def _update_child_in_mempool(
        prevout: Prevout,
        outq: Optional['asyncio.Queue[Prevout]'] = None) -> None:
    '''
    Checks a prevout spent by a mempool transaction to see if the tx was
      confirmed or dropped
    Args:
        prevout (Prevout): a prevout spent by a mempool tx
        outq      (Queue): the external-facing notification queue
    '''
    utils.LOGGER.info(
        'checking mempool spend status of {}:{}'.format(
            prevout['outpoint']['tx_id'],
            prevout['outpoint']['index']))

    # check cache and server for the tx
    tx_entry_or_none = await tx_cache.get_tx(prevout['spent_by'])

    # NB: if we don't get tx info back, that means the tx was evicted
    #     from the mempool, we should update the prevout to unspent
    if tx_entry_or_none is None:
        utils.LOGGER.info('marking prevout unspent {}:{}'.format(
            prevout['outpoint']['tx_id'],
            prevout['outpoint']['index']))
        asyncio.ensure_future(set_prevout_to_unspent(prevout, outq))
        return

    # NB: if the tx entry is not confirmed, return
    tx_entry = cast(TransactionEntry, tx_entry_or_none)
    if tx_entry['confirmed_in'] is None or tx_entry['confirmed_height'] < 0:
        return

    # NB: we'll accept 10 confirmations as VERY unlikely to roll back
    #     if it has 10+ confs, update its `spent_at` and store
    #     we should also notify the frontend that we found it
    best_header = headers.find_heaviest()[0]
    confirmed_in = cast(str, tx_entry['confirmed_in'])
    if (best_header['height'] - tx_entry['confirmed_height']) >= 10:
        utils.LOGGER.info('marking prevout spent {}:{}'.format(
            prevout['outpoint']['tx_id'],
            prevout['outpoint']['index']))
        coro = set_prevout_to_spent(prevout, confirmed_in, outq)
        asyncio.ensure_future(coro)


async def _update_children_in_mempool(
        outq: Optional['asyncio.Queue[Prevout]'] = None) -> None:
    '''
    Periodically checks the DB for mempool txns that spend our prevouts
    If the txn has moved from the mempool and been confirmed 10x we update it
    Args:
        outq      (Queue): the external-facing notification queue
    '''
    while True:
        # NB: sleep at the end so that this runs once at startup
        # find all the prevouts that claim to be spent by a tx in the mempool
        child_in_mempool = prevouts.find_spent_by_mempool_tx()
        if len(child_in_mempool) != 0:
            utils.LOGGER.info('found {} prevouts spent by mempool txns'.format(
                len(child_in_mempool)))
        for prevout in child_in_mempool:
            asyncio.ensure_future(_update_child_in_mempool(prevout, outq))

        # run again in 10 minutes
        # TODO: run this each time we see a new block
        await asyncio.sleep(600)


async def _update_prevout_never_confirmed():
    '''Every 10 minutes, check for prevouts created by'''
    while True:
        unconfirmed_creator = prevouts.find_unconfirmed_creator()

        if len(unconfirmed_creator) != 0:
            utils.LOGGER.info(
                'found {} prevouts created by unconfirmed txns'.format(
                    len(unconfirmed_creator)))

        for prevout in unconfirmed_creator:
            asyncio.ensure_future(_check_confirmation(prevout))

        # TODO: run this each time we see a new block
        await asyncio.sleep(600)


async def _check_confirmation(prevout: Prevout):
    # if we can't find it, it is dropped from the mempool
    tx_response = await electrum.get_tx_verbose(prevout['outpoint']['tx_id'])

    if tx_response is None:
        utils.LOGGER.info('deleting unconfirmed prevout {}:{}'.format(
            prevout['outpoint']['tx_id'],
            prevout['outpoint']['index']))
        prevouts.delete_prevout(prevout)
