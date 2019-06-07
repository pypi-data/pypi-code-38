# -*- encoding: utf8 -*-


import sqlite3

conn = None


def get_connection(sqlite_db_path) -> sqlite3.Connection:
    global conn
    if conn is None:
        conn = sqlite3.connect(sqlite_db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
    return conn

