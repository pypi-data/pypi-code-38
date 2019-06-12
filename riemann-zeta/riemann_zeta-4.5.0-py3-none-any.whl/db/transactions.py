import sqlite3

from zeta.db import connection

from riemann import tx
from riemann import utils as rutils
from riemann.encoding import addresses as addr

from typing import cast, List, Optional
from zeta.zeta_types import InputEntry, OutputEntry, TransactionEntry


def transaction_from_row(row: sqlite3.Row) -> TransactionEntry:
    '''
    Instantiates a TransactionEntry from a db row
    '''
    return TransactionEntry(
        tx_id=row['tx_id'],
        lock_time=row['lock_time'],
        version=row['version'],
        num_tx_ins=row['num_tx_ins'],
        num_tx_outs=row['num_tx_outs'],
        total_value_out=row['total_value_out'],
        confirmed_in=row['confirmed_in'],
        confirmed_height=row['confirmed_height'],
        merkle_verified=True if row['merkle_verified'] == 1 else False,
        hex=row['hex'],
        object=tx.Tx.from_hex(row['hex']))


def validate_transaction(t: TransactionEntry) -> bool:
    '''
    Validates a transaction entry
    Checks that the info is consistent with the tx object
    Checks that the confirmed_in and confirmed_height are consistent
        Either the confirmed height is negative and there's no confirming hash
        Or there confirmed height is >0 and there's a confirming hash
    Args:
        t (TransactionEntry): the entry to validate
    Returns:
        (bool): True for valid, False otherwise
    '''
    t_obj = t['object']
    out_value = sum(
        [rutils.le2i(out.value) for out in t_obj.tx_outs])

    return (
        t['tx_id'] == t_obj.tx_id.hex()
        and t['lock_time'] == rutils.le2i(t_obj.lock_time)
        and t['version'] == rutils.le2i(t_obj.version)
        and t['num_tx_ins'] == len(t_obj.tx_ins)
        and t['num_tx_outs'] == len(t_obj.tx_outs)
        and t['total_value_out'] == out_value
        and t['object'].hex() == t['hex']
        and ((t['confirmed_height'] in [-2, -1] and t['confirmed_in'] is None)
             or (t['confirmed_height'] > 0 and t['confirmed_in'] is not None)))


def flatten_outputs(transaction: TransactionEntry) -> List[OutputEntry]:
    '''
    Turns the outputs of a transaction into output entries for DB storage
    Args:
        transaction (TransactionEntry): the transaction entry
    Returns:
        List(OutputEntry): the flattened outputs
    '''
    tx_obj = transaction['object']
    outputs: List[OutputEntry] = []
    for i in range(len(tx_obj.tx_outs)):
        value = rutils.le2i(tx_obj.tx_outs[i].value)
        try:
            address = addr.from_output_script(tx_obj.tx_outs[i].output_script)
        except ValueError:
            # NB: 0 value things are op returns
            #     other things are weird af
            address = 'OP_RETURN' if value == 0 else 'NONSTANDARD'
        outputs.append(OutputEntry(
            included_in=transaction['tx_id'],
            value=rutils.le2i(tx_obj.tx_outs[i].value),
            pubkey_script=tx_obj.tx_outs[i].output_script,
            address=address,
            outpoint='{}{}'.format(tx_obj.tx_id_le.hex(),
                                   rutils.i2le_padded(i, 4).hex())))
    return outputs


def flatten_inputs(transaction: TransactionEntry) -> List[InputEntry]:
    '''
    Turns the inputs of a transaction into input entries for DB storage
    Args:
        transaction (TransactionEntry): the transaction entry
    Returns:
        List(OutputEntry): the flattened inputs
    '''
    tx_obj = transaction['object']
    inputs: List[InputEntry] = []
    for i in range(len(tx_obj.tx_ins)):
        inputs.append(InputEntry(
            spent_by=transaction['tx_id'],
            outpoint=tx_obj.tx_ins[i].outpoint.hex(),
            tx_id=tx_obj.tx_ins[i].outpoint.tx_id[::-1].hex(),
            idx=rutils.le2i(tx_obj.tx_ins[i].outpoint.index),
            sequence=rutils.le2i(tx_obj.tx_ins[i].sequence)))
    return inputs


def store_transaction(
        transaction: TransactionEntry) -> bool:
    '''
    Stores a transaction entry in the db
    Args:
        transaction (TransactionEntry): the transaction entry
    Returns:
        (bool): true if successful, error otherwise
    '''
    if not validate_transaction(transaction):
        raise ValueError('invalid transaction')

    if find_by_tx_id(transaction['tx_id']) is not None:
        return True

    outs = flatten_outputs(transaction)
    ins = flatten_inputs(transaction)

    tmp_tx = cast(dict, transaction.copy())
    tmp_tx.pop('object')

    c = connection.get_cursor()
    try:
        c.execute(
            '''
            INSERT INTO transactions VALUES (
                :tx_id,
                :lock_time,
                :version,
                :num_tx_ins,
                :num_tx_outs,
                :total_value_out,
                :confirmed_in,
                :confirmed_height,
                :merkle_verified,
                :hex)
            ''', tmp_tx)
        for o in outs:
            c.execute(
                '''
                INSERT INTO tx_outs VALUES (
                    :included_in,
                    :value,
                    :pubkey_script,
                    :address,
                    :outpoint)
                ''', o)
        for i in ins:
            c.execute(
                '''
                INSERT OR REPLACE INTO tx_ins VALUES (
                    :spent_by,
                    :outpoint,
                    :tx_id,
                    :idx,
                    :sequence)
                ''', i)
        connection.commit()
        return True
    finally:
        c.close()


def update_transaction_confirmation(transaction: TransactionEntry) -> bool:
    '''
    Updates the tx confirmation information
    Args:
        transaction (TransactionEntry): the transaction to update in the db
    Returns:
        (bool): True for success, error otherwise
    '''
    if not validate_transaction(transaction):
        raise ValueError('invalid transaction')
    c = connection.get_cursor()
    try:
        c.execute(
            '''
            UPDATE transactions
                SET confirmed_in = :confirmed_in,
                    confirmed_height = :confirmed_height
                WHERE tx_id = :tx_id
            ''',
            {
                'confirmed_in': transaction['confirmed_in'],
                'confirmed_height': transaction['confirmed_height'],
                'tx_id': transaction['tx_id']
            })
        connection.commit()
        return True
    finally:
        c.close()


def update_merkle_verified(transaction: TransactionEntry) -> bool:
    '''
    Updates the "merkle_verified" boolean when we have verified
      a merkle inclusion proof.
    Args:
        transaction (TransactionEntry): the transaction to update in the db
    Returns:
        (bool): True for success, error otherwise

    '''
    if not validate_transaction(transaction):
        raise ValueError('invalid transaction')
    c = connection.get_cursor()
    try:
        c.execute(
            '''
            UPDATE transactions
                SET merkle_verified = :merkle_verified
                WHERE tx_id = :tx_id
            ''',
            {
                'merkle_verified': transaction['merkle_verified'],
                'tx_id': transaction['tx_id']
            })
        connection.commit()
        return True
    finally:
        c.close()


def find_by_tx_id(tx_id: str) -> Optional[TransactionEntry]:
    '''
    Finds a tx by its id.
    tx_ids are unique, so either we have it or we don't
    Args:
        tx_id (str): the id of the tx
    Returns:
        (Optional(TransactionEntry)): the entry
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT * FROM transactions
            WHERE tx_id = :tx_id
            ''',
            {'tx_id': tx_id})
        for a in res:
            # little hacky. returns first entry
            # we know there can only be one
            return transaction_from_row(a)
        return None
    finally:
        c.close()


def find_by_spent_outpoint(outpoint: str) -> List[TransactionEntry]:
    '''
    Finds txns by an outpoint they spent
    Args:
        outpoint (str): the spent outpoint
    Returns:
        (List(TransactionEntry)): any txns we know of that spent that outpoint
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
            WHERE tx_id IN
                (SELECT spent_by FROM tx_ins
                 WHERE outpoint = :outpoint)
            ''',
            {'outpoint': outpoint})]
    finally:
        c.close()


def find_by_output(value: int, address: str) -> List[TransactionEntry]:
    '''
    Finds txns by an output they created
    Args:
        value   (int): the output value
        address (str):
    Returns:
        (List(TransactionEntry)): any txns we know of that made that output
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
            WHERE tx_id IN
                (SELECT included_in FROM tx_outs
                 WHERE value = :value
                 AND address = :address)
            ''',
            {'value': value, 'address': address})]
    finally:
        c.close()


def find_by_confirmed_height(height: int) -> List[TransactionEntry]:
    '''
    Finds txns by the height at which they were confirmed
    Args:
        height (str): the confirmed height
    Returns:
        (List(TransactionEntry)): any txns we know of confirmed at that height
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
            WHERE confirmed_height = :height
            ''',
            {'height': height})]
    finally:
        c.close()


def find_by_confirming_block(block_hash: str) -> List[TransactionEntry]:
    '''
    Finds txns by the block in which they were confirmed
    Args:
        block_hash (str): the block we care about
    Returns:
        (List(TransactionEntry)): any txns we know of confirmed in that block
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
            WHERE confirmed_in = :block_hash
            ''',
            {'block_hash': block_hash})]
    finally:
        c.close()


def find_by_hex(hex_tx: str) -> Optional[TransactionEntry]:
    '''
    Finds tx entries by the hex string of their transaction
    Args:
        hex_tx (str) the transaction as hex
    Returns:
        (Optional(TransactionEntry)): the tx entry or None
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT * FROM transactions
            WHERE hex = :hex_tx
            ''',
            {'hex_tx': hex_tx})
        for a in res:
            # little hacky. returns first entry
            # we know there can only be one
            return transaction_from_row(a)
        return None
    finally:
        c.close()


def find_confirmed_but_unverified() -> List[TransactionEntry]:
    '''
    Finds transactions with a confirmation height greater than -1,
      with unverified merkle proofs
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE merkle_verified = 0
                AND confirmed_height > -1
            ''')]
    finally:
        c.close()


def find_not_in_main_chain() -> List[TransactionEntry]:
    '''
    Finds transactions that have a "confirmed_in" attribute
    But the confirmed_in is NOT in our current view of the main chain
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE confirmed_in NOT NULL
                AND confirmed_in NOT IN
                (SELECT hash FROM best_chain)
            ''')]
    finally:
        c.close()


def find_confirmed_in_main_chain() -> List[TransactionEntry]:
    '''
    Finds transactions that are confirmed in the best chain
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE confirmed_in NOT NULL
                AND confirmed_in IN
                (SELECT hash FROM best_chain)
            ''')]
    finally:
        c.close()


def find_unconfirmed() -> List[TransactionEntry]:
    '''
    Finds transactions that are known but not yet confirmed
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
            WHERE confirmed_height IN (-1, -2)
            ''')]
    finally:
        c.close()


def find_conflict_set(t: TransactionEntry) -> List[TransactionEntry]:
    '''
    Finds all transactions that conflict with a provided transaction
    The innermost query gets all outpoints spent by the tx.
    The next query gets all tx_ids spending those outpoints
    The outermost query gets all transactions with those tx_ids
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE tx_id IN
                (SELECT spent_by FROM tx_ins WHERE outpoint IN
                    (SELECT outpoint FROM tx_ins WHERE spent_by = :tx_id))
            ''', {'tx_id': t['tx_id']})]

    finally:
        c.close()


def find_all_conflicts() -> List[TransactionEntry]:
    '''
    Finds all transactions with conflicts
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE tx_id IN
                (SELECT spent_by FROM tx_ins WHERE outpoint IN
                    (SELECT outpoint FROM tx_ins
                     GROUP BY outpoint HAVING COUNT(*) > 1))
            ''')]
    finally:
        c.close()


def find_can_confirm() -> List[TransactionEntry]:
    '''
    Finds all transactions in the mempool that could still be confirmed
    '''
    can_confirm: List[TransactionEntry] = []
    for te in find_unconfirmed():

        # don't recheck things we've seen
        if te in can_confirm:
            continue

        conflicts = find_conflict_set(te)
        if max([c['confirmed_height'] for c in conflicts]) < 0:
            can_confirm.extend([c for c in conflicts if c not in can_confirm])

    return can_confirm


def find_can_not_confirm() -> List[TransactionEntry]:
    '''
    Finds all transactions in the mempool that can't still be confirmed
    '''
    can_not_confirm: List[TransactionEntry] = []
    for tx_entry in find_unconfirmed():

        # don't recheck things we've seen
        if tx_entry in can_not_confirm:
            continue  # pragma: nocover

        conflicts = find_conflict_set(tx_entry)

        # if there's a confirmed conflict
        if max([c['confirmed_height'] for c in conflicts]) >= 0:
            # the mempool txns can't be confirmed
            can_not_confirm.extend(
                [c for c in conflicts if c['confirmed_height'] < 0
                 and c not in can_not_confirm])

    return can_not_confirm  # deduplicate


def find_tracked_transactions() -> List[TransactionEntry]:
    '''
    Finds transactions associated with an address in the DB
    We shortcut this by finding txns that create or consume prevouts
    Because we know prevouts are _ours_
    '''
    c = connection.get_cursor()
    try:
        return [transaction_from_row(a) for a in c.execute(
            '''
            SELECT * FROM transactions
                WHERE tx_id IN
                    (SELECT tx_id FROM prevouts)
                OR tx_id IN
                    (SELECT spent_by FROM prevouts)
            ''')]
    finally:
        c.close()
