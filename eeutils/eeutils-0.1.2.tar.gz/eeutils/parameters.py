# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

import click

from .utils import with_cr


class DatabaseParameter(click.ParamType):
    name = 'str'

    def complete(self, ctx, incomplete):
        def _filter_db(dbname):
            return incomplete in dbname

        try:
            cmd = [
                "psql", "-l", "-A", "-F','", "-R';'", "-t"
            ]
            proc = Popen(cmd, stdout=PIPE)
            proc.wait()
            bases_data = proc.stdout.read().decode()
            databases = [row.split(",")[0].strip("'") for
                         row in bases_data.split(";")]
            return filter(_filter_db, databases)
        except BaseException as e:
            return []


class ModelParameter(click.ParamType):
    name = 'str'

    def complete(self, ctx, incomplete):
        database = ctx.params.get('database')

        @with_cr
        def _fetch_models(database, cr=False):
            if not cr:
                return []

            query = """
            SELECT im.model
            FROM ir_model im
            WHERE im.model ~* %(model)s
            ORDER BY im.model
            """
            query_vals = {
                'model': incomplete,
            }
            cr.execute(query, query_vals)
            fetch = cr.fetchall()
            return [row[0] for row in fetch]

        return _fetch_models(database=database)
