import sqlite3

from riemann import utils as rutils
from riemann.encoding import addresses as addr
from riemann.script import serialization as script_ser

from zeta import crypto
from zeta.db import connection

from zeta.zeta_types import AddressEntry
from typing import cast, List, Union, Optional


def address_from_row(row: sqlite3.Row) -> AddressEntry:
    '''
    Turns a row object into an AddressEntry dict
    '''
    a: AddressEntry = {
        'address': row['address'],
        'script': row['script'],
        'script_pubkeys': pubkeys_from_script(row['script'])
    }
    return a


def validate_address(address: AddressEntry) -> bool:
    '''
    Validates the address data structure
    '''
    try:
        h = addr.parse_hash(address['address'])
        if address['script'] == b'':
            return True

        if address['script_pubkeys'] != pubkeys_from_script(address['script']):
            return False

        if h in [rutils.sha256(address['script']),    # p2wsh
                 rutils.hash160(address['script'])]:  # p2sh
            return True
    except (ValueError, TypeError, KeyError):
        pass

    return False


def pubkeys_from_script(script: bytes) -> List[str]:
    '''
    guess-parses pubkeys from a serialized bitcoin script
    '''
    res: List[str] = []
    s = script_ser.deserialize(script)
    for token in s.split():
        if crypto.is_pubkey(token):
            res.append(token)
    return res


def store_address(address: Union[str, AddressEntry]) -> bool:
    '''
    stores an address in the db
    accepts a string address
    '''
    a: AddressEntry

    if type(address) is str:
        a = {
            'address': cast(str, address),
            'script': b'',
            'script_pubkeys': []
        }
    else:
        a = cast(AddressEntry, address)

    if not validate_address(a):
        raise ValueError('invalid address entry')

    c = connection.get_cursor()
    try:
        c.execute(
            '''
            INSERT OR REPLACE INTO addresses VALUES (
                :address,
                :script)
            ''',
            a)

        # NB: we track what pubkeys show up in what scripts so we can search
        for pubkey in a['script_pubkeys']:
            c.execute(
                '''
                INSERT OR REPLACE INTO pubkey_to_script VALUES (
                    :pubkey,
                    :script)
                ''',
                {'pubkey': pubkey, 'script': a['script']})
        connection.commit()
        return True
    finally:
        c.close()


def find_associated_pubkeys(script: bytes) -> List[str]:
    '''
    looks up pubkeys associated with a script
    somewhat redundant with pubkeys_from_script
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT pubkey FROM pubkey_to_script
            WHERE script = :script
            ''',
            {'script': script})
        return [r['pubkey'] for r in res]
    finally:
        c.close()


def find_by_address(address: str) -> Optional[AddressEntry]:
    '''
    Finds an AddressEntry for the address if it exists, returns None otherwise
    '''
    c = connection.get_cursor()
    try:
        res = c.execute(
            '''
            SELECT * from addresses
            WHERE address = :address
            ''',
            {'address': address})
        for a in res:
            # little hacky. returns first entry
            # we know there can only be one
            return address_from_row(a)
        return None
    finally:
        c.close()


def find_by_script(script: bytes) -> List[AddressEntry]:
    '''
    Finds all AddressEntries with the corresponding Script
    '''
    c = connection.get_cursor()
    try:
        res = [address_from_row(r) for r in c.execute(
            '''
            SELECT * FROM addresses
            WHERE script = :script
            ''',
            {'script': script})]
        return res
    finally:
        c.close()


def find_by_pubkey(pubkey: str) -> List[AddressEntry]:
    '''
    Finds all AddressEntries whose script includes the specified pubkey
    '''
    c = connection.get_cursor()
    try:
        res = [address_from_row(r) for r in c.execute(
            '''
            SELECT * FROM addresses
            WHERE script IN
                (SELECT script FROM pubkey_to_script
                 WHERE pubkey = :pubkey)
            ''',
            {'pubkey': pubkey})]
        return res
    finally:
        c.close()


def find_all_addresses() -> List[str]:
    '''
    Finds all addresses that we're tracking
    '''
    c = connection.get_cursor()
    try:
        return [r['address'] for r in c.execute(
            '''
            SELECT address FROM addresses
            '''
        )]
    finally:
        c.close()
