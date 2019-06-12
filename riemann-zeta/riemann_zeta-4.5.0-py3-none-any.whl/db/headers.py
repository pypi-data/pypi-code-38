import math
import sqlite3

from riemann import utils as rutils

from zeta.db import connection

from zeta.zeta_types import Header
from typing import cast, List, Optional, Tuple, Union


def header_from_row(row: sqlite3.Row) -> Header:
    '''
    Does what it says on the tin
    '''
    return cast(Header, dict((k, row[k]) for k in row.keys()))


def check_work(header: Header) -> bool:
    '''
    Checks a header's work against its work target
    Args:
        (dict): The header to check
    Returns:
        (bool): True if the header has enough work, otherwise false
    '''
    nbits = bytes.fromhex(cast(str, header['nbits']))
    return int(cast(str, header['hash']), 16) <= make_target(nbits)


def make_target(nbits: bytes) -> int:
    '''
    converts an nbits from a header into the target
    Args:
        nbits (bytes): the 4-byte nbits bytestring
    Returns:
        (int): the target threshold
    '''
    exponent = rutils.be2i(nbits[-1:]) - 3
    return math.floor(rutils.le2i(nbits[:-1]) * 0x100 ** (exponent))


def parse_difficulty(nbits: bytes) -> int:
    '''
    converts an nbits from a header into the difficulty
    Args:
        nbits (bytes): the 4-byte nbits bytestring
    Returns:
        (int): the difficulty (no decimals)
    '''
    return make_target(b'\xff\xff\x00\x1d') // make_target(nbits)


def parse_header(header: str) -> Header:
    '''
    Parses a header to a dict
    Args:
        header (str): hex formatted 80 byte header
    Returns:
        dict:
            hash        (str): the header hash 0000-first
            version     (int): the block version as an int
            prev_block  (str): the previous block hash 0000-first
            merkle_root (str): the block transaction merkle tree root
            timestamp   (int): the block header timestamp
            nbits       (str): the difficulty bits
            nonce       (str): the nonce
            difficulty  (int): the difficulty as an int
            hex         (str): the full header as hex
            height      (int): the block height (always 0)
    '''
    if len(header) != 160:
        raise ValueError('Invalid header received')
    as_bytes = bytes.fromhex(header)
    nbits = as_bytes[72:76]
    return {
        'hash': rutils.hash256(bytes.fromhex(header))[::-1].hex(),
        'version': rutils.le2i(as_bytes[0:4]),
        'prev_block': as_bytes[4:36][::-1].hex(),
        'merkle_root': as_bytes[36:68].hex(),
        'timestamp': rutils.le2i(as_bytes[68:72]),
        'nbits': nbits.hex(),
        'nonce': as_bytes[76:80].hex(),
        'difficulty': parse_difficulty(nbits),
        'hex': header,
        'height': 0,
        'accumulated_work': 0
    }


def batch_store_header(h: List[Union[Header, str]]) -> bool:
    '''
    Stores a batch of headers in the database
    Args:
        header list(str or dict): parsed or unparsed header
    Returns:
        (bool): true if succesful, false if error
    '''
    # TODO: Refactor and improve
    c = connection.get_cursor()

    headers: List[Header] = [normalize_header(header) for header in h]
    headers = list(filter(check_work, headers))
    headers = _trim_batch(headers)
    for header in headers:
        _find_parent_in_batch(header, headers)

    try:
        for header in headers:
            c.execute(
                '''
                INSERT OR REPLACE INTO headers VALUES (
                    :hash,
                    :version,
                    :prev_block,
                    :merkle_root,
                    :timestamp,
                    :nbits,
                    :nonce,
                    :difficulty,
                    :hex,
                    :height,
                    :accumulated_work)
                ''',
                (header))
        connection.commit()
        return True
    finally:
        c.close()


def normalize_header(header: Union[Header, str]) -> Header:
    '''
    Normalizes string header inputs to Header objects
    Args:
        header (str or Header): the string or object input
    Returns:
        (Header): the normalized header
    '''
    if isinstance(header, str):
        parsed_header = parse_header(cast(str, header))
    else:
        parsed_header = cast(Header, header)
    parsed_header['height'] = 0
    parsed_header['accumulated_work'] = 0
    return parsed_header


def _trim_batch(batch: List[Header]) -> List[Header]:
    # NB: this block finds the last header for which we know a parent
    #     it discards headers earlier in the batch
    #     this pretty much assumes batches are ordered
    for i in range(len(batch)):
        parent = find_by_hash(
            cast(str, batch[i]['prev_block']))
        if parent:
            batch[i]['height'] = parent['height'] + 1
            batch[i]['accumulated_work'] = (
                parent['accumulated_work']
                + batch[0]['difficulty'])
            batch = batch[i:]
            break
    return batch


def _find_parent_in_batch(header: Header, batch: List[Header]) -> None:
    '''
    Finds a parent in the current batch
    Args:
        header      (Header): the header we care about
        batch (List(Header)): the current batch
    '''
    # NB: this block checks if the header has a parent in the current batch
    #     it populates the height and accumulated work fields if so
    if header['height'] != 0:
        return

    results = list(filter(
        lambda k: k['hash'] == header['prev_block'],
        batch))

    if len(results) == 0 or results[0]['height'] == 0:
        return

    parent = results[0]
    header['height'] = parent['height'] + 1
    header['accumulated_work'] = \
        parent['accumulated_work'] + header['difficulty']


def try_to_associate_height_and_work(header: Header) -> Header:
    '''
    Tries to associate height and work with a header based
        on a parent in the db
    Args:
        header (Header): the header we're looking for info on
    Returns:
        (Header): the modified header
    '''
    parent_height, parent_work = parent_height_and_work(header)
    if parent_height != 0:
        header['height'] = parent_height + 1
        header['accumulated_work'] = parent_work + header['difficulty']
    else:
        header['height'] = 0
        header['accumulated_work'] = 0
    return header


def parent_height_and_work(header: Header) -> Tuple[int, int]:
    '''
    Find the header's parent in the DB and return its height and work
    Args:
        header (Header): the child header
    Returns:
        (int, int): the parent's height and work, both 0 if not found
    '''
    parent_or_none = find_by_hash(header['prev_block'])
    if parent_or_none is not None:
        parent = cast(Header, parent_or_none)
        parent_work = parent['accumulated_work']
        parent_height = parent['height']
        return parent_height, parent_work
    else:
        return 0, 0


def store_header(header: Union[Header, str]) -> bool:
    '''
    Stores a header in the database
    Args:
        header (str or dict): parsed or unparsed header
    Returns:
        (bool): true if succesful, false if error
    '''
    if isinstance(header, str):
        header = parse_header(header)

    if not check_work(header):
        raise ValueError('Invalid header')

    if header['height'] == 0:
        try_to_associate_height_and_work(header)

    c = connection.get_cursor()
    try:
        c.execute(
            '''
            INSERT OR REPLACE INTO headers VALUES (
                :hash,
                :version,
                :prev_block,
                :merkle_root,
                :timestamp,
                :nbits,
                :nonce,
                :difficulty,
                :hex,
                :height,
                :accumulated_work)
            ''',
            (header))
        connection.commit()
        return True
    finally:
        c.close()


def find_by_height(height: int) -> List[Header]:
    '''
    Finds headers by blockheight. Can return more than 1
    Args:
        height (str): integer blockheight
    Returns:
        dict:
            hash        (str): the header hash 0000-first
            version     (int): the block version as an int
            prev_block  (str): the previous block hash 0000-first
            merkle_root (str): the block transaction merkle tree root
            timestamp   (int): the block header timestamp
            nbits       (str): the difficulty bits
            nonce       (str): the nonce
            difficulty  (int): the difficulty as an int
            hex         (str): the full header as hex
            height      (int): the block height
    '''
    c = connection.get_cursor()
    try:
        res = [header_from_row(r) for r in c.execute(
            '''
            SELECT * FROM headers
            WHERE height = :height
            ''',
            {'height': height})]
        return res
    finally:
        c.close()


def find_by_hash(hash: str) -> Optional[Header]:
    '''
    Finds a header by hash
    Args:
        has (str): 0000-first header hash
    Returns:
        dict:
            hash        (str): the header hash 0000-first
            version     (int): the block version as an int
            prev_block  (str): the previous block hash 0000-first
            merkle_root (str): the block transaction merkle tree root
            timestamp   (int): the block header timestamp
            nbits       (str): the difficulty bits
            nonce       (str): the nonce
            difficulty  (int): the difficulty as an int
            hex         (str): the full header as hex
            height      (int): the block height
    '''
    c = connection.get_cursor()
    try:
        res = [header_from_row(r) for r in c.execute(
            '''
            SELECT * FROM headers
            WHERE hash = :hash
            ''',
            {'hash': hash})]
        if len(res) != 0:
            return res[0]
        return None
    finally:
        c.close()


def find_highest() -> List[Header]:
    '''
    Finds the highest headers we know of.
    This is not very useful
    Returns:
        (List(Header)): the highest headers
    '''
    c = connection.get_cursor()
    try:
        res = [header_from_row(r) for r in c.execute(
            '''
            SELECT * FROM headers
            WHERE height = (SELECT max(height) FROM headers)
            '''
        )]
        return res
    finally:
        c.close()


def find_heaviest() -> List[Header]:
    '''
    Finds the heaviest blocks we know of
    This returns a list, because between difficulty resets the
        blocks will accumulate work at the same rate
    Generally we'll take the 0th entry and then it'll work out over time
    Returns:
        (List(Header)): the heaviest headers
    '''
    c = connection.get_cursor()
    try:
        res = [header_from_row(r) for r in c.execute(
            '''
            SELECT * FROM headers
            WHERE accumulated_work =
                (SELECT max(accumulated_work) FROM headers)
            '''
        )]
        return res
    finally:
        c.close()


def find_main_chain_block_at_height(height: int) -> Optional[Header]:
    '''
    Finds a block in the main chain at a specific height
    Args:
        height (int): the height we're looking for
    Returns:
        Optional(Header): the main chain block at that height or None
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT * FROM headers WHERE hash IN
                (SELECT hash FROM best_chain
                WHERE height = :height)
            ''', {'height': height})
        for h in res:
            return header_from_row(h)
        return None
    finally:
        c.close()


def mark_best_at_height(best: Header) -> bool:
    '''
    Marks a header the best at its height by storing its hash in the
      best_chain table.
    Args:
        best (Header); the header we believe is best at the height
    '''
    c = connection.get_cursor()
    current_or_none = find_main_chain_block_at_height(best['height'])
    if current_or_none is not None:
        current = cast(Header, current_or_none)
        if current['hash'] == best['hash']:
            return False
    try:
        c.execute(
            '''
            INSERT OR REPLACE INTO best_chain VALUES (
                :height,
                :hash)
            ''', {'height': best['height'], 'hash': best['hash']})
        connection.commit()
        return True
    finally:
        c.close()


def set_chain_tip() -> bool:
    '''
    Deletes best chain enties above the height of a transaction
    '''
    c = connection.get_cursor()
    try:
        c.execute('''
        DELETE FROM best_chain WHERE height >
            (SELECT height FROM HEADERS WHERE accumulated_work =
                (SELECT max(accumulated_work) FROM headers)
             LIMIT 1)
        ''')
        connection.commit()
        return True
    finally:
        c.close()


def find_main_chain_gap_ends() -> List[int]:
    c = connection.get_cursor()
    try:
        return [r['height'] for r in c.execute('''
            SELECT a.height
            FROM best_chain a
            WHERE NOT EXISTS
                (SELECT b.height
                 FROM best_chain b
                 WHERE b.height = a.height-1)
            AND a.height >
                (SELECT MIN(c.height)
                 FROM best_chain c)
             ''')]
    finally:
        c.close()
