import os
import sys
import sqlite3

from typing import Optional

# TODO: Clean all this up and make better


def ensure_directory(p) -> None:  # pragma: nocover
    '''
    Creates the PATH data directory if it does not already exist
    '''
    if not os.path.exists(p):
        os.makedirs(p)


if sys.platform.startswith('win'):
    PATH_ROOT = os.path.expandvars(r'%LOCALAPPDATA%')  # pragma: nocover
else:
    PATH_ROOT = os.path.expanduser('~')  # pragma: nocover

DEFAULT_PATH = os.path.join(PATH_ROOT, '.summa', 'zeta')

PATH: str
DB_NAME: str
CHAIN_NAME: str

DB_PATH: str
CONN: sqlite3.Connection


def init_conn(
        path: Optional[str] = None,
        db_name: Optional[str] = None,
        chain_name: Optional[str] = None):  # pragma: nocover
    global PATH
    global DB_NAME
    global CHAIN_NAME
    global DB_PATH
    global CONN

    if path:
        PATH = path
    else:
        PATH = os.environ.get('ZETA_DB_PATH', DEFAULT_PATH)
    if db_name:
        DB_NAME = db_name
    else:
        DB_NAME = os.environ.get('ZETA_DB_NAME', 'zeta')
    if chain_name:
        CHAIN_NAME = chain_name
    else:
        CHAIN_NAME = os.environ.get('ZETA_NETWORK', 'bitcoin_main')

    # Set the path and make sure it exists
    DB_PATH = os.path.join(PATH, '{}_{}.db'.format(DB_NAME, CHAIN_NAME))
    ensure_directory(PATH)

    CONN = sqlite3.connect(DB_PATH)
    CONN.row_factory = sqlite3.Row

    # make sure the tables exist
    ensure_directory(PATH)
    ensure_tables()


def commit():
    return CONN.commit()


def get_cursor() -> sqlite3.Cursor:
    return CONN.cursor()


def ensure_tables() -> bool:
    '''

    Returns:
        (bool): true if table exists/was created, false if there's an exception
    '''
    c = get_cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS headers(
                hash TEXT PRIMARY KEY,
                version INTEGER,
                prev_block TEXT,
                merkle_root TEXT,
                timestamp INTEGER,
                nbits TEXT,
                nonce TEXT,
                difficulty INTEGER,
                hex TEXT,
                height INTEGER,
                accumulated_work INTEGER)
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS addresses(
                address TEXT PRIMARY KEY,
                script BLOB NOT NULL DEFAULT (x''))
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pubkey_to_script(
                pubkey TEXT,
                script BLOB,
                FOREIGN KEY(script) REFERENCES addresses(script))
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS keys(
                pubkey TEXT PRIMARY KEY,
                privkey BLOB,
                derivation TEXT NOT NULL DEFAULT '',
                chain TEXT NOT NULL DEFAULT 'btc',
                address TEXT,
                FOREIGN KEY(address) REFERENCES addresses(address))
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prevouts(
                outpoint TEXT PRIMARY KEY,
                tx_id TEXT UNIQUE,
                idx INTEGER,
                value INTEGER,
                spent_at INTEGER NOT NULL DEFAULT -2,
                spent_by TEXT NOT NULL DEFAULT '',
                address TEXT,
                FOREIGN KEY(address) REFERENCES addresses(address))
            ''')  # default -2 for not yet spent. electrum uses -1 for mempool
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions(
                tx_id TEXT,
                lock_time INTEGER,
                version INTEGER,
                num_tx_ins INTEGER,
                num_tx_outs INTEGER,
                total_value_out INTEGER,
                confirmed_in TEXT,
                confirmed_height INTEGER NOT NULL DEFAULT -2,
                merkle_verified INTEGER NOT NULL DEFAULT 0,
                hex TEXT)
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tx_ins(
                spent_by TEXT,
                outpoint TEXT,
                tx_id TEXT,
                idx INTEGER,
                sequence INTEGER,
                FOREIGN KEY(spent_by) REFERENCES transactions(tx_id))
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tx_outs(
                included_in TEXT,
                value INTEGER,
                pubkey_script BLOB,
                address TEXT,
                outpoint TEXT,
                FOREIGN KEY(included_in) REFERENCES transactions(tx_id))
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS best_chain(
                height INTEGER UNIQUE NOT NULL,
                hash TEXT,
                FOREIGN KEY(hash) REFERENCES headers(hash))
            ''')
        commit()
        return True

    finally:
        c.close()


def print_tables() -> None:  # pragma: nocover
    c = get_cursor()
    res = c.execute('''
       SELECT name FROM sqlite_master WHERE type="table"
       ''')
    print([a for row in res for a in row])
