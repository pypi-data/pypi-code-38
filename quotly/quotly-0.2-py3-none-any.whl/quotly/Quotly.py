import os
import sqlite3

from quotly.Quote import Quote


class Quotly:
    def __init__(self):
        if not os.path.exists('data'):
            os.mkdir('data')

        self.conn = sqlite3.connect('data/quotes.db')
        self.initialize()

        print('> Quotly successfully started! Let the quoting begin!')

    def initialize(self):
        cur = self.conn.cursor()

        cur.execute("create table if not exists quotes "
                    "(id integer primary key autoincrement, quote text not null , author text)")

        self.conn.commit()

    def store_quote(self, quote, *targets):
        cur = self.conn.cursor()

        t = []
        if len(targets[0]) > 0:
            for targ in targets[0]:
                t.append(targ)

        t.extend([''] * (1 - len(t)))
        cur.execute(
            "insert into quotes (quote, author) "
            "values (?, ?)", (quote, t[0]))

        self.conn.commit()

        # fetch latest quote
        cur.execute("select quote, author "
                    "from quotes order by id desc limit 1")

        q = Quote(cur.fetchone())
        print('> Quote stored: {0}'.format(q))
        return q

    def fetch_quote(self):
        cur = self.conn.cursor()

        cur.execute("select quote, author "
                    "from quotes order by random() limit 1")

        return Quote(cur.fetchone())

    def fetch_quote_with_targets(self, *targets):
        cur = self.conn.cursor()

        t = list(targets)
        t.extend([''] * (1 - len(targets)))
        cur.execute("select quote, author "
                    "from quotes "
                    "where author == (?) "
                    "order by random() limit 1", t[0])

        return Quote(cur.fetchone())

    def __del__(self):
        self.conn.close()
