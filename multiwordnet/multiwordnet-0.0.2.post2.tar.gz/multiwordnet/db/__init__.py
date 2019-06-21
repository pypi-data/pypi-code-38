""" Contains the WordNet databases  """

import codecs
import os
import sqlite3
import sys
from sqlite3 import IntegrityError, OperationalError

from tqdm import tqdm

module = sys.modules['multiwordnet.db'].__path__[0]


def connect(language, database):
    """ Connects to a database """

    try:
        if os.path.exists(f"{module}/{language}/{language}_{database}.db"):
            cursor = sqlite3.connect(f"{module}/{language}/{language}_{database}.db").cursor()
        else:
            raise OperationalError
    except OperationalError:
        cursor = None
    finally:
        return cursor


def compile(language, *tables):
    if not tables:
        tables = [filename.split('_', maxsplit=1)[1].replace('.sql', '') for filename in os.listdir(f"{module}/{language}/") if filename.endswith('.sql')]

    for table in tables:
        f = codecs.open(f"{module}/{language}/{language}_{table}.sql", encoding='utf-8')
        if not f:
            continue
        try:
            os.remove(f"{module}/{language}/{language}_{table}.db")
        except OSError:
            pass
        db = sqlite3.connect(f"{module}/{language}/{language}_{table}.db").cursor()

        if not db:
            continue

        db.execute("PRAGMA synchronous = OFF")
        db.execute("PRAGMA journal_mode = MEMORY")
        for sql in tqdm(f.readlines(), ncols=80, desc=f"{language}_{table}.sql"):
            if not(sql.startswith('#') or sql == '\n'):
                try:
                    db.executescript(sql)
                except IntegrityError:
                    continue
        f.close()
