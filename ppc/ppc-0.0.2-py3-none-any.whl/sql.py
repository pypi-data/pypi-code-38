import logging
import sqlite3


class SQLError(Exception):
    def __init__(self, message):
        self.message = message


class SQLCache:
    def __init__(self, database, source):
        self.database = database
        self.source = source
        self.conn = sqlite3.connect(self.database)
        self._init_db()
        self._pragma_table_info()

    def __getattr__(self, name):
        return getattr(self.source, name)

    def _policies_table(self):
        # TODO need to cleanup cur? with open or something?
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM sqlite_master WHERE type = "table" AND tbl_name = "policies"')
        return cur.fetchone()

    def _create_db(self):
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE policies(hash TEXT PRIMARY KEY, ' + ','.join(self.source.policies.unique_keys) + ')')
        cur.execute('CREATE TABLE syncs(id INTEGER PRIMARY KEY, at DEFAULT CURRENT_TIMESTAMP)')
        cur.execute('CREATE TABLE s_to_ps(sync_id INTEGER, hash_id TEXT, FOREIGN KEY(sync_id) REFERENCES syncs(id), FOREIGN KEY(hash_id) REFERENCES policies(hash))')

    def _init_db(self):
        if not self._policies_table():
            if self.source is None:
                raise SQLError("No database cache, no data source")

            self._create_db()

    def _pragma_table_info(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM PRAGMA_TABLE_INFO("policies");')
        self.tbl_policies_pragma = cur.fetchall()

    @property
    def column_names(self):
        return [item[1] for item in self.tbl_policies_pragma]

    def _insert_sync(self):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO syncs DEFAULT VALUES')
        self.conn.commit()
        return cur.lastrowid

    def _insert_policy(self, policy, sync_id):
        cols = ','.join(policy.keys)
        binds = ','.join(['?' for _ in policy.values])
        insert = 'INSERT INTO policies(hash,' + cols + ') VALUES(?,' + binds + ')'

        cur = self.conn.cursor()
        vals = policy.values
        vals.insert(0, policy.hash)

        try:
            cur.execute(insert, vals)
        except sqlite3.IntegrityError as ie:
            logging.debug(f"Seen policy before {ie}")

        cur.execute("INSERT INTO s_to_ps(sync_id, hash_id) VALUES(?,?)", (sync_id, policy.hash))
        return policy.hash

    def _insert_policies(self, sync_id):
        return [self._insert_policy(p, sync_id) for p in self.source.policies]

    def sync(self):
        sync_id = self._insert_sync()
        self._insert_policies(sync_id)
        self.conn.commit()
