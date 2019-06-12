import math
import sqlite3

from riemann import utils as rutils

from zeta import connection
from zeta.utils import Header

from typing import cast, List, Optional, Tuple, Union


def header_from_row(row: sqlite3.Row) -> Header:
    '''
    Does what it says on the tin
    '''
    return cast(Header, dict(zip(row.keys(), row)))


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


# TODO: use the new expiremental typed dict to clean up all this
def batch_store_header(h: List[Union[Header, str]]) -> bool:
    '''
    Stores a batch of headers in the database
    Args:
        header list(str or dict): parsed or unparsed header
    Returns:
        (bool): true if succesful, false if error
    '''
    c = connection.get_cursor()

    headers: List[Header] = []

    for i in range(len(h)):
        if isinstance(h[i], str):
            headers.append(parse_header(h[i]))  # type: ignore
        else:
            headers.append(cast(Header, h[i]))
        headers[i]['height'] = 0
        headers[i]['accumulated_work'] = 0

    headers = list(filter(check_work, headers))

    # NB: this block finds the last header for which we know a parent
    #     it discards headers earlier in the batch
    #     this pretty much assumes batches are ordered
    for i in range(len(headers)):
        parent = find_by_hash(
            cast(str, headers[i]['prev_block']))  # type: ignore
        if parent:
            headers[i]['height'] = parent['height'] + 1  # type: ignore
            headers[i]['accumulated_work'] = (
                parent['accumulated_work']  # type: ignore
                + headers[0]['difficulty'])  # type: ignore
            headers = headers[i:]
            break

    # NB: this block checks if the header has a parent in the current batch
    #     it populates the height and accumulated work fields if so
    for header in headers:
        if header['height'] == 0:
            results = list(filter(  # type: ignore
                lambda k: k['hash'] == header['prev_block'],
                headers))
            if len(results) != 0 and results[0]['height'] > 0:  # type: ignore
                header['height'] = results[0]['height'] + 1  # type: ignore
                header['accumulated_work'] = (
                    results[0]['accumulated_work']  # type: ignore
                    + header['difficulty'])  # type: ignore

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
    except Exception:
        raise
        return False
    finally:
        c.close()


def parent_height_and_work(header: Header) -> Tuple[int, int]:
    parent = find_by_hash(cast(str, header['prev_block']))
    if parent:
        parent_work = cast(int, parent['accumulated_work'])
        parent_height = cast(int, parent['height'])
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
        return False

    if header['height'] == 0:
        parent_height, parent_work = parent_height_and_work(header)
        if parent_height != 0 and parent_work != 0:
            header['height'] = parent_height + 1  # type: ignore
            header['accumulated_work'] = (
                parent_work + header['difficulty'])  # type: ignore
        else:
            header['height'] = 0
            header['accumulated_work'] = 0

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
    except Exception:
        raise
        return False
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
    except Exception:
        raise
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
        else:
            return None
    except Exception:
        raise
    finally:
        c.close()


def find_highest() -> List[Header]:
    c = connection.get_cursor()
    try:
        res = [header_from_row(r) for r in c.execute(
            '''
            SELECT * FROM headers
            WHERE height = (SELECT max(height) FROM headers)
            '''
        )]
        return res
    except Exception:
        raise
    finally:
        c.close()


def find_heaviest() -> List[Header]:
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
    except Exception:
        raise
    finally:
        c.close()
