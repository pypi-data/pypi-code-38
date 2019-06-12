import asyncio

from zeta import electrum, utils
from zeta.db import checkpoint, headers

from typing import cast, List, Optional, Union
from zeta.zeta_types import Header, ElectrumHeaderNotification, ElectrumHeader


async def sync(
        outq: Optional['asyncio.Queue[Header]'] = None,
        network: str = 'bitcoin_main') -> None:  # pragma: nocover
    '''
    Starts all header tracking processes
    1. subscribe to headers feed (track chain tip)
    2. catch up to the servers' view of the chain tip
    3. clean up any headers that didn't fit a chain when we found them
    '''
    utils.LOGGER.info('starting chain sync tasks')
    best_known_block_height = _initial_setup(network)
    utils.LOGGER.info('heaviest block at {}'.format(best_known_block_height))
    # NB: assume there hasn't been a 10 block reorg
    asyncio.ensure_future(_track_chain_tip(outq))
    asyncio.ensure_future(_catch_up(best_known_block_height))
    asyncio.ensure_future(_maintain_db())


def _initial_setup(network: str) -> int:  # pragma: nocover
    '''
    Ensures the database directory exists, and tables exist
    Then set the highest checkpoint, and return its height
    '''
    # Get the highest checkpoint
    # NB: normally it is bad to follow height
    #     but this is an explicitly trusted source
    latest_checkpoint = max(
        checkpoint.CHECKPOINTS[network],
        key=lambda k: k['height'])
    headers.store_header(latest_checkpoint)

    return cast(int, headers.find_heaviest()[0]['height'])


async def _track_chain_tip(
        outq: Optional['asyncio.Queue[Header]'] = None) \
        -> None:  # pragma: nocover
    '''
    subscribes to headers, and starts the header queue handler
    '''
    q: asyncio.Queue[ElectrumHeaderNotification] = asyncio.Queue()
    await electrum.subscribe_to_headers(q)
    asyncio.ensure_future(_header_queue_handler(q, outq))


async def _header_queue_handler(
        inq: 'asyncio.Queue[ElectrumHeaderNotification]',
        outq: Optional['asyncio.Queue[Header]'] = None) \
        -> None:  # pragma: nocover
    '''
    Handles a queue of incoming headers. Ingests each individually
    Args:
        q (asyncio.Queue): the queue of headers awaiting ingestion
    '''
    header_dict: ElectrumHeader

    while True:
        electrum_response = await inq.get()
        # NB: the initial result and subsequent notifications are inconsistent
        #     so we try to unwrap it from a list
        try:
            header_dict = cast(List[ElectrumHeader], electrum_response)[0]
        except Exception:
            header_dict = cast(ElectrumHeader, electrum_response)
        header = headers.parse_header(header_dict['hex'])
        utils.LOGGER.info('got new header: {}'.format(header['hash']))
        # store the header and send it to the outq
        headers.store_header(header)
        if outq is not None:
            await outq.put(header)


async def _catch_up(from_height: int) -> None:  # pragma: nocover
    '''
    Catches the chain tip up to latest by batch requesting headers
    Schedules itself at a new from_height if not complete yet
    Increments by 2014 to pad against the possibility of multiple off-by-ones
    Args:
        from_height (int): height we currently have, and want to start from
    '''
    electrum_response = await electrum.get_headers(
        start_height=max(from_height - 10, 0),
        count=2016)

    utils.LOGGER.info(
        'catch-up task got {} new headers'.format(electrum_response['count']))

    # NB: we requested 2016. If we got back 2016, it's likely there are more
    if electrum_response['count'] == 2016:
        asyncio.ensure_future(_catch_up(from_height - 10 + 2014))
    _process_header_batch(electrum_response['hex'])


async def _maintain_db() -> None:  # pragma: nocover
    '''
    Loop that runs some DB maintenance tasks
    Restoring them attempts to connect them to another known header
    '''
    utils.LOGGER.info('starting chain DB maintenance')
    while True:
        utils.LOGGER.info('running chain DB maintenance tasks')
        asyncio.ensure_future(check_for_floating_headers())
        asyncio.ensure_future(mark_best_chain())
        asyncio.ensure_future(_check_for_main_chain_gaps())

        # TODO: run this on each new header instead
        await asyncio.sleep(600)


async def mark_best_chain() -> None:
    '''
    Marks headers in the best chain.
    We do this by finding the heaviest block we know of and then traversing
        recursively up its ancestors until we reach a common ancestor
        or a missing link (which is unexpected unless we hit our checkpoint)
    '''
    tip = headers.find_heaviest()[0]
    headers.set_chain_tip()

    utils.LOGGER.info(
        'marking best chain. current tip is {}'.format(tip['hash']))

    await mark_best_chain_from(tip)


async def _check_for_main_chain_gaps() -> None:
    '''Checks the main chain for gaps'''
    gaps_ends = headers.find_main_chain_gap_ends()
    for height in gaps_ends:
        asyncio.ensure_future(_fill_in_main_chain_gap(height))


async def _fill_in_main_chain_gap(height: int) -> None:
    '''Fills in a miain chain gap'''
    gap_end_or_none = headers.find_main_chain_block_at_height(height)
    if gap_end_or_none is None:
        return
    gap_end = cast(Header, gap_end_or_none)
    parent_or_none = headers.find_by_hash(gap_end['prev_block'])
    if parent_or_none is None:
        return
    parent = cast(Header, parent_or_none)

    utils.LOGGER.info('filling in best chain gap ending at {}'.format(height))
    await mark_best_chain_from(parent)


async def mark_best_chain_from(current: Header) -> None:
    '''Marks the best chain backwards from a known height'''
    count = 0

    while headers.mark_best_at_height(current):
        if count > 300:
            count = 0
            await asyncio.sleep(2)  # prevent blocking everything
        utils.LOGGER.info('marking height {} best block {}'.format(
            current['height'], current['hash']))

        next_or_none = headers.find_by_hash(current['prev_block'])
        if next_or_none is None:
            utils.LOGGER.error('failed to find parent in best chain')
            break
        current = cast(Header, next_or_none)
        count += 1


async def check_for_floating_headers() -> None:
    '''
    This checks for floating headers (those at height 0)
    And then tries to find their place
    '''
    # NB: 0 means no known parent
    floating = headers.find_by_height(0)
    if len(floating) != 0:
        utils.LOGGER.info(
            're-storing {} floating headers'.format(len(floating)))

    # NB: this will attempt to find their parent and fill in height/accdiff
    for header in floating:
        headers.store_header(header)


def _process_header_batch(electrum_hex: str) -> None:  # pragma: nocover
    '''
    Processes a batch of headers and sends to the DB for storage
    Args:
        electrum_hex (str): The 'hex' attribute of electrum's getheaders res
    '''
    # NB: this comes as a single hex string with all headers concatenated
    blob = bytes.fromhex(electrum_hex)
    header_list: List[Union[Header, str]]
    header_list = [blob[i:i + 80].hex() for i in range(0, len(blob), 80)]
    utils.LOGGER.info('storing {} new headers'.format(len(header_list)))
    headers.batch_store_header(header_list)
