import asyncio
from riemann import tx
from riemann import utils as rutils

from zeta import electrum, utils
from zeta.db import addresses, headers, transactions

from zeta.zeta_types import Header, TransactionEntry
from typing import Any, cast, Dict, List, Optional, Tuple, Union


_OUTQ: Optional['asyncio.Queue[TransactionEntry]'] = None


async def _send_to_outq(
        transaction: TransactionEntry) \
        -> None:  # pragma: nocover
    '''
    Sends a transaction entry to the outq if it exists
    '''
    if _OUTQ is not None:
        await cast(asyncio.Queue, _OUTQ).put(transaction)


async def sync(
        outq: Optional['asyncio.Queue[TransactionEntry]'] = None) \
        -> None:  # pragma: nocover
    '''
    Starts syncing tasks ands store the outq if any
    Args:
        outq (asyncio.Queue): the outbound message queue
    '''
    global _OUTQ
    _OUTQ = outq
    asyncio.ensure_future(_get_unknown_txns())
    asyncio.ensure_future(_maintain_db())


async def _get_unknown_txns() -> None:  # pragma: nocover
    '''
    Goes over the history of all known addresses and gets unknown txns
    Does them iteratively so we're not spamming the server all at once
    This is not a "critical" function so we're okay with waiting
        a few extra seconds
    '''
    for address in addresses.find_all_addresses():
        history = await electrum.get_history(address)
        for entry in history:
            asyncio.ensure_future(get_tx(entry['tx_hash']))


async def _maintain_db() -> None:  # pragma: nocover
    '''
    Maintains the DB by periodically searching for unconfirmed txns and
      checking on them
    '''
    utils.LOGGER.info('starting tx cache maintenance tasks')
    asyncio.ensure_future(_maintain_unconfirmed())
    asyncio.ensure_future(_maintain_unverified())
    asyncio.ensure_future(_maintain_confirmed_in_orphan())


async def _maintain_unverified() -> None:  # pragma: nocover
    '''
    Periodically checks the DB for unverified txns, and attempts to erify them
    '''
    while True:
        unverified = transactions.find_confirmed_but_unverified()

        if len(unverified) != 0:
            utils.LOGGER.info(
                'found {} unverified txns'.format(len(unverified)))

        for transaction in unverified:
            asyncio.ensure_future(check_merkle_proof(transaction))
        # TODO: run this on each block instead
        await asyncio.sleep(600)


async def _maintain_unconfirmed() -> None:  # pragma: nocover
    '''
    Checks unconfirmed txns for confirmations
    '''
    while True:
        at_height_negative_one = transactions.find_by_confirmed_height(-1)
        at_height_negative_two = transactions.find_by_confirmed_height(-2)

        # concatenate lists
        unconfirmed = at_height_negative_one + at_height_negative_two

        if len(unconfirmed) != 0:
            utils.LOGGER.info('checking status of {} unconfirmed txns'.format(
                len(unconfirmed)))

        for transaction in unconfirmed:
            asyncio.ensure_future(_check_for_confirmations(transaction))

        # TODO: trigger this on a new block
        await asyncio.sleep(600)  # Again in 10 minutes


async def _maintain_confirmed_in_orphan() -> None:
    '''
    Checks confirmed transactions for txns confirmed in an orphan block
    Marks them unconfirmed and then checks for confirmations
    '''
    while True:
        orphaned = transactions.find_not_in_main_chain()

        if len(orphaned) != 0:
            utils.LOGGER.info('found {} txns in orphaned blocks'.format(
                len(orphaned)))

        for orphan in orphaned:
            # Set it to unconfirmed
            orphan['confirmed_in'] = None
            orphan['confirmed_height'] = -1
            transactions.update_transaction_confirmation(orphan)

            # update listener
            asyncio.ensure_future(_send_to_outq(orphan))

            # check it for confirmations
            asyncio.ensure_future(_check_for_confirmations(orphan))

        # TODO: trigger this on a new block
        await asyncio.sleep(600)


async def _process_new_tx_entry(transaction: TransactionEntry) -> None:
    '''
    Stores a tx entry in the db, and sends it to the outq
    Args:
        transaction (TransactionEntry): the new transaction
    '''
    # store it in the db
    transactions.store_transaction(transaction)
    await _send_to_outq(transaction)


async def _check_for_confirmations(transaction: TransactionEntry) -> None:
    '''
    Check a tx entry for confirmations stores in the DB if there's an update
    Args:
        transaction (TransactionEntry): the tx to check
    '''

    utils.LOGGER.debug(
        'checking for confirmations: {}'.format(transaction['tx_id']))

    # retireve it from electrum
    electrum_tx_or_none = await electrum.get_tx_verbose(transaction['tx_id'])

    # if electrum doesn't know of it, kick it back for later
    if electrum_tx_or_none is None:
        return

    electrum_tx = cast(Dict[str, Any], electrum_tx_or_none)

    # if no blockhash, it's not confirmed. Wait for later
    if 'blockhash' not in electrum_tx:
        return

    # if no header, it's not confirmed that we know of. Wait for later
    header_or_none = headers.find_by_hash(electrum_tx['blockhash'])
    if header_or_none is None:
        return

    header = cast(Header, header_or_none)
    transaction['confirmed_in'] = electrum_tx['blockhash']
    transaction['confirmed_height'] = header['height']
    transaction['merkle_verified'] = False

    utils.LOGGER.debug('found {} in block {}'.format(
        transaction['tx_id'],
        header['hash']))

    transactions.update_transaction_confirmation(transaction)
    await _send_to_outq(transaction)


async def get_tx(tx_id: str) -> Optional[TransactionEntry]:
    '''
    Gets a transaction entry. Checks the DB first, and then requests it from
      electrum servers. Returns None if not found
    Args:
        tx_id (str): the transaction id
    Returns:
        (TransactionEntry): the transaction entry. None if not found
    '''
    utils.LOGGER.debug('getting tx {}'.format(tx_id))

    # Check the DB
    tx_or_none = transactions.find_by_tx_id(tx_id)
    if tx_or_none is not None:
        utils.LOGGER.debug('found in cache: {}'.format(tx_id))
        return cast(TransactionEntry, tx_or_none)

    # retireve it from electrum
    electrum_tx_or_none = await electrum.get_tx_verbose(tx_id)

    # if electrum doesn't know of it, return None because we can't find it
    if electrum_tx_or_none is None:
        utils.LOGGER.debug('server does not know: {}'.format(tx_id))
        return None

    # put it into our DB format
    electrum_tx = cast(Dict[str, Any], electrum_tx_or_none)
    tx_entry = electrum_verbose_tx_to_transaction_entry(electrum_tx)

    asyncio.ensure_future(_process_new_tx_entry(tx_entry))

    utils.LOGGER.debug('retrieved tx from server: {}'.format(tx_id))
    return tx_entry


def electrum_verbose_tx_to_transaction_entry(
        electrum_tx: Dict[str, Any]) -> TransactionEntry:
    '''
    Converts a verbose electrum response to a transaction entry
    Populates all information we have
    Args:
        electrum_tx (dict): an electrum protocol verbose tx response
    '''
    entry = normalize_transaction(electrum_tx['hex'])
    if 'blockhash' not in electrum_tx:
        entry['confirmed_height'] = -1
        entry['confirmed_in'] = None
        entry['merkle_verified'] = False
    else:
        header_or_none = headers.find_by_hash(electrum_tx['blockhash'])
        if header_or_none is None:
            entry['confirmed_height'] = -1
            entry['confirmed_in'] = None
            entry['merkle_verified'] = False
        else:
            header = cast(Header, header_or_none)
            entry['confirmed_in'] = electrum_tx['blockhash']
            entry['confirmed_height'] = header['height']
            entry['merkle_verified'] = False

    # Schedule proof checking
    asyncio.ensure_future(check_merkle_proof(entry))

    return entry


async def check_merkle_proof(
        transaction: TransactionEntry) -> None:
    '''
    Checks whether a merkle proof verifies a tx's inclusion in a block we know
    Stores result in DB if True
    Args:
        transaction (TransactionEntry): the tx entry to check
    '''
    # unknown confirming height
    if (transaction['confirmed_height'] < 0
            or transaction['confirmed_in'] is None):
        utils.LOGGER.debug('not confirmed in merkle verification: {}'.format(
            transaction['tx_id']))
        return

    # not enoguh confirmations in heaviest chain
    if (transaction['confirmed_height'] + 10
            > headers.find_heaviest()[0]['height']):
        utils.LOGGER.debug('need more confs in merkle verification: {}'.format(
            transaction['tx_id']))
        return

    # see if we know of the header
    header_or_none = headers.find_by_hash(
        cast(str, transaction['confirmed_in']))

    # if the header is unknown, we can't verify
    if header_or_none is None:
        utils.LOGGER.debug('unknown header in merkle verification: {}'.format(
            transaction['tx_id']))
        return

    # if we know of the header, grab its merkle root
    header = cast(Header, header_or_none)
    block_root = header['merkle_root']

    # get the merkle proof from the network
    electrum_response = await electrum.get_merkle(
        transaction['tx_id'],
        transaction['confirmed_height'])
    merkle_proof = electrum_response['merkle']
    pos = electrum_response['pos']

    # verify it
    result = verify_electrum_merkle_proof(
        tx_id=transaction['tx_id'],
        merkle_proof=merkle_proof,
        pos=pos,
        block_root=block_root)

    # if succesful, store the verified result
    if result:
        transaction['merkle_verified'] = True
        transactions.update_merkle_verified(transaction)
        await _send_to_outq(transaction)
    else:
        utils.LOGGER.debug('proof failed in merkle verification: {}'.format(
            transaction['tx_id']))


def verify_electrum_merkle_proof(
        tx_id: str,
        merkle_proof: List[str],
        pos: int,
        block_root: str) -> bool:
    '''
    Transforms and then verifies a proof from electrum
    Args:
        tx_id              (str): the hex tx_id in BE format
        merkle_proof (List(str)): the electrum merkle proof list
        pos                (int): the electrum position number
        block_root         (str): the block header merkle root in LE format
    Returns:
        (bool): True for verified correctly, False otherwise
    '''
    proof, idx = transform_electrum_proof(tx_id, merkle_proof, pos, block_root)
    return verify_proof(bytes.fromhex(proof), idx)


def transform_electrum_proof(
        tx_id: str,
        merkle_proof: List[str],
        pos: int,
        block_root: str) -> Tuple[str, int]:
    '''
    I wrote the verify_proof logic previously and I am VERY averse to rewriting
    So we transform the proof here and then verify it
    Args:
        tx_id              (str): the hex tx_id in BE format
        merkle_proof (List(str)): the electrum merkle proof list
        pos                (int): the electrum position number
        block_root         (str): the block header merkle root in LE format
    Returns:
        (str): the proof as a hex string
        (int): the index number
    '''
    proof = bytearray()
    proof.extend(bytes.fromhex(tx_id)[::-1])
    for tx_id in merkle_proof:
        proof.extend(bytes.fromhex(tx_id)[::-1])

    proof.extend(bytes.fromhex(block_root))

    return (proof.hex(), pos + 1)


def verify_proof(proof: bytes, index: int):
    '''
    verifies a merkle leaf occurs at a specified index given a merkle proof
    Args:
        proof (bytes): the proof as a bytestring. tx_id first, merkle root last
        index   (int): the index of the tx in the block. 1-indexed :(
    Returns:
        (bool): True for verified correctly, False otherwise
    '''
    index = index  # This is 1 indexed
    # TODO: making creating and verifying indexes the same
    root = proof[-32:]
    current = proof[0:32]

    # For all hashes between first and last
    for i in range(1, len(proof) // 32 - 1):
        # If the current index is even,
        # The next hash goes before the current one
        if index % 2 == 0:
            current = rutils.hash256(
                proof[i * 32: (i + 1) * 32]
                + current
            )
            # Halve and floor the index
            index = index // 2
        else:
            # The next hash goes after the current one
            current = rutils.hash256(
                current
                + proof[i * 32: (i + 1) * 32]
            )
            # Halve and ceil the index
            index = index // 2 + 1
    # At the end we should have made the root
    if current != root:
        return False
    return True


def normalize_transaction(
        transaction: Union[tx.Tx, str]) -> TransactionEntry:
    '''
    Turns a raw tx or transaction object into a TransactionEntry
    Args:
        transaction (hex_str or tx.Tx): raw or object transaction
    Returns:
        (TransactionEntry): normalized tx entry
    '''
    if type(transaction) is str:
        t = tx.Tx.from_hex(cast(str, transaction))
    else:
        t = cast(tx.Tx, transaction)
    return tx_object_to_transaction_entry(t)


def tx_object_to_transaction_entry(transaction: tx.Tx) -> TransactionEntry:
    '''
    Turns a riemann tx object into a TransactionEntry
    Args:
        transaction (riemann.tx.Tx): the tx as an object
    Returns:
        (TransactionEntry): the normalized tx entry
    '''
    out_value = sum([rutils.le2i(out.value) for out in transaction.tx_outs])
    return TransactionEntry(
        tx_id=transaction.tx_id.hex(),
        lock_time=rutils.le2i(transaction.lock_time),
        version=rutils.le2i(transaction.version),
        num_tx_ins=len(transaction.tx_ins),
        num_tx_outs=len(transaction.tx_outs),
        total_value_out=out_value,
        confirmed_in='',
        confirmed_height=-2,
        merkle_verified=False,
        hex=transaction.hex(),
        object=transaction)
