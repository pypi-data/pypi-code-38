from psqlgraph import * # noqa
from sqlalchemy import * # noqa


def main():
    import IPython
    import os

    db_host = os.environ['PG_HOST']
    db_name = os.environ['PG_NAME']
    db_user = os.environ['PG_USER']
    db_pass = os.environ['PG_PASS']
    dict_url = os.environ.get('DICTIONARY_URL')
    if dict_url:
        from dictionaryutils import DataDictionary, dictionary
        d = DataDictionary(url=dict_url)
        dictionary.init(d)
    from gdcdatamodel import models as md
    g = PsqlGraphDriver(host=db_host, user=db_user,
                        password=db_pass, database=db_name)
    ss = g.session_scope
    with g.session_scope() as session:
        IPython.embed()
