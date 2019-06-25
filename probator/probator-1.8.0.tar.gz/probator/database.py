from sqlservice import SQLClient, declarative_base

from probator import app_config

Model = declarative_base()


def get_db_connection():
    return SQLClient({
        'SQL_DATABASE_URI': app_config.database_uri,
        'SQL_POOL_RECYCLE': 300,
        'SQL_POOL_PRE_PING': True
    }, model_class=Model)


db = get_db_connection()
