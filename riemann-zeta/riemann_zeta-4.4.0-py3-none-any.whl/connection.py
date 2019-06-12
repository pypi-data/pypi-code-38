import os
import sys
import sqlite3


# TODO: Clean all this up and make better

def ensure_directory() -> None:
    '''
    Creates the PATH data directory if it does not already exist
    '''
    if not os.path.exists(PATH):
        os.makedirs(PATH)


if sys.platform.startswith('win'):
    PATH_ROOT = os.path.expandvars(r'%LOCALAPPDATA%')
else:
    PATH_ROOT = os.path.expanduser('~')

DEFAULT_PATH = os.path.join(PATH_ROOT, '.summa', 'zeta')

# Prefer the env variables
PATH = os.environ.get('ZETA_DB_PATH', DEFAULT_PATH)
DB_NAME = os.environ.get('ZETA_DB_NAME', 'zeta.db')

# Set the path and make sure it exists
DB_PATH = os.path.join(PATH, DB_NAME)
ensure_directory()

CONN = sqlite3.connect(DB_PATH)
CONN.row_factory = sqlite3.Row


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
        commit()
        return True
    except Exception as e:
        print(e, str(e))
        return False
    finally:
        c.close()


def print_tables() -> None:
    c = get_cursor()
    res = c.execute('''
       SELECT name FROM sqlite_master WHERE type="table"
       ''')
    print([a for row in res for a in row])
