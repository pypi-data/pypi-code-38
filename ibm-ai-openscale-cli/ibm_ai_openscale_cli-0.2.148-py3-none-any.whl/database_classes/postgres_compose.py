# coding=utf-8
from ibm_ai_openscale_cli.database_classes.postgres import Postgres

class PostgresCompose(Postgres):

    def __init__(self, credentials):
        user = credentials['uri'].split('@')[0].split('//')[1].split(':')[0]
        password = credentials['uri'].split('@')[0].split('//')[1].split(':')[1]
        hostname = credentials['uri'].split('@')[1].split(':')[0]
        port = credentials['uri'].split('@')[1].split(':')[1].split('/')[0]
        dbname = credentials['uri'].split('@')[1].split('/')[1]
        super().__init__(user, password, hostname, port, dbname)
