import sqlite3

from riemann import utils as rutils
from riemann.encoding import addresses as addr

from zeta import utils
from zeta.db import connection
from zeta.zeta_types import Outpoint, Prevout, PrevoutEntry

from typing import List, Optional


def prevout_from_row(row: sqlite3.Row) -> Prevout:
    res: Prevout = {
        'outpoint': Outpoint(
            tx_id=row['tx_id'],
            index=row['idx']),
        'value': row['value'],
        'spent_at': row['spent_at'],
        'spent_by': row['spent_by'],
        'address': row['address']}
    return res


def _flatten_prevout(prevout: Prevout) -> PrevoutEntry:
    outpoint = '{tx_id}{index}'.format(
        tx_id=utils.reverse_hex(prevout['outpoint']['tx_id']),
        index=rutils.i2le_padded(prevout['outpoint']['index'], 4).hex())
    return {
        'outpoint': outpoint,
        'tx_id': prevout['outpoint']['tx_id'],
        'idx': prevout['outpoint']['index'],
        'value': prevout['value'],
        'spent_at': prevout['spent_at'],
        'spent_by': prevout['spent_by'],
        'address': prevout['address']
    }


def validate_prevout(prevout: Prevout) -> bool:
    '''
    Validates the internal structure of a prevout
    '''
    try:
        if prevout['value'] <= 0:
            return False
        addr.parse_hash(prevout['address'])
    except Exception:
        return False

    return True


def store_prevout(prevout: Prevout) -> bool:
    '''
    Stores a prevout in the database
    Args:
        prevout (dict): the prevout
    Return:
        (bool): true if successful, false if error
    '''
    c = connection.get_cursor()

    if not validate_prevout(prevout):
        raise ValueError('invalid prevout')

    try:
        flattened = _flatten_prevout(prevout)
        c.execute(
            '''
            INSERT OR REPLACE INTO prevouts VALUES (
                :outpoint,
                :tx_id,
                :idx,
                :value,
                :spent_at,
                :spent_by,
                :address)
            ''',
            flattened)
        connection.commit()
        return True
    finally:
        c.close()


def batch_store_prevout(prevout_list: List[Prevout]) -> bool:
    '''
    Stores a batch of prevouts in the DB. Uses only one transaction
    Args:
        prevout_list (list(Prevout)): the prevouts to store
    Returns:
        (bool): True if prevouts were stored, false otherwise
    '''
    c = connection.get_cursor()

    for prevout in prevout_list:
        if not validate_prevout(prevout):
            raise ValueError('invalid prevout in batch')

    try:
        flattened_list = list(map(_flatten_prevout, prevout_list))
        for prevout_entry in flattened_list:
            c.execute(
                '''
                INSERT OR REPLACE INTO prevouts VALUES (
                    :outpoint,
                    :tx_id,
                    :idx,
                    :value,
                    :spent_at,
                    :spent_by,
                    :address)
                ''',
                prevout_entry)
        connection.commit()
        return True
    finally:
        c.close()


def find_by_address(address: str) -> List[Prevout]:
    '''
    Finds prevouts by associated address
    One address may have many prevouts
    Args:
        address (str):
    '''
    c = connection.get_cursor()

    try:
        return [prevout_from_row(r) for r in c.execute(
            '''
            SELECT * FROM prevouts
            WHERE address = :address
            ''',
            {'address': address})]
    finally:
        c.close()


def find_by_tx_id(tx_id: str) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE tx_id = :tx_id
            ''',
            {'tx_id': tx_id}
        )]
        return res
    finally:
        c.close()


def find_by_outpoint(outpoint: Outpoint) -> Optional[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE tx_id = :tx_id
              AND idx = :index
            ''',
            outpoint
        )]
        for p in res:
            # little hacky. returns first entry
            # we know there can only be one
            return p
        return None
    finally:
        c.close()


def find_all_unspents() -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE spent_at = -2
            '''
        )]
        return res
    finally:
        c.close()


def find_by_child(child_tx_id: str) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE spent_by = :child_tx_id
            ''',
            {'child_tx_id': child_tx_id}
        )]
        return res
    finally:
        c.close()


def find_by_value_range(
        lower_value: int,
        upper_value: int,
        unspents_only: bool = True) -> List[Prevout]:
    c = connection.get_cursor()
    try:
        # I don't like this.
        # figure out how to do this without string format
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE value <= :upper_value
              AND value >= :lower_value
              AND spent_at {operator} -2
            '''.format(operator=('==' if unspents_only else '!=')),
            {'upper_value': upper_value,
             'lower_value': lower_value})]
        return res
    finally:
        c.close()


def find_spent_by_mempool_tx() -> List[Prevout]:
    '''
    Finds prevouts that have been spent by a tx in the mempool
    Useful for checking if a tx can be replaced or has confirmed
    '''
    c = connection.get_cursor()
    try:
        # I don't like this.
        # figure out how to do this without string format
        res = [prevout_from_row(p) for p in c.execute(
            '''
            SELECT * from prevouts
            WHERE spent_at == -1
            ''')]
        return res
    finally:
        c.close()


def check_for_known_outpoints(
        outpoint_list: List[Outpoint]) -> List[Outpoint]:
    '''
    Finds all prevouts we know of from a list of outpoints
    Useful for checking whether the DB already knows about specific prevouts
    '''
    # NB: We want to flatten the outpoint to look it up in the DB
    flattened_list: List[str] = []
    for o in outpoint_list:
        flat_outpoint = '{tx_id}{index}'.format(
            tx_id=utils.reverse_hex(o['tx_id']),
            index=rutils.i2le_padded(o['index'], 4).hex())
        flattened_list.append(flat_outpoint)

    c = connection.get_cursor()
    try:
        question_marks = ', '.join(['?' for _ in range(len(outpoint_list))])
        cursor = c.execute(
            '''
            SELECT tx_id, idx FROM prevouts
            WHERE outpoint IN ({question_marks})
            '''.format(question_marks=question_marks),
            flattened_list)
        res = [Outpoint(tx_id=p['tx_id'], index=p['idx']) for p in cursor]
        return res
    finally:
        c.close()


def find_all() -> List[Prevout]:
    '''
    Finds all prevouts
    '''
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(r) for r in c.execute(
            '''
            SELECT * FROM prevouts
            ''')]
        return res
    finally:
        c.close()


def find_unconfirmed_creator() -> List[Prevout]:
    '''
    Finds outpoints where we have not confirmed their creator
    '''
    c = connection.get_cursor()
    try:
        res = [prevout_from_row(r) for r in c.execute(
            '''
            SELECT * FROM prevouts
            WHERE outpoint NOT IN (
                SELECT outpoint FROM tx_outs
            )
            OR outpoint IN (
                SELECT outpoint FROM tx_outs
                WHERE included_in IN (
                    SELECT tx_id FROM transactions
                    WHERE confirmed_height < 0))
            ''')]
        return res
    finally:
        c.close()


def delete_prevout(prevout: Prevout) -> bool:
    '''
    Deletes a prevout from the database
    '''
    flat_outpoint = '{tx_id}{index}'.format(
        tx_id=utils.reverse_hex(prevout['outpoint']['tx_id']),
        index=rutils.i2le_padded(prevout['outpoint']['index'], 4).hex())
    c = connection.get_cursor()
    try:
        c.execute(
            '''
            DELETE FROM prevouts WHERE outpoint = :outpoint
            ''', {'outpoint': flat_outpoint})
        return True
    finally:
        c.close()
