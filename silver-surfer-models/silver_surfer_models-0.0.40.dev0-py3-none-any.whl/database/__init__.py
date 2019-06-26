import os

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient


def _get_ssm_parameters():
    result = {}
    session = boto3.Session(region_name='us-east-1')
    ssm = session.client('ssm')
    ssm_parameters = ssm.get_parameters(
        Names=[
            'mysqlHost',
            'mysqlUser',
            'mysqlPassword',
            'mysqlDB',
            'mongoHost',
            'mongoUser',
            'mongoPassword',
            'mongoDB',
        ],
        WithDecryption=True | False
    )['Parameters']
    for parameter in ssm_parameters:
        result[parameter['Name']] = parameter['Value']
    return result


def _get_credentials():
    result = {
        'mysqlHost': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'mysqlUser': os.getenv('MYSQL_USER', 'root'),
        'mysqlPassword': os.getenv('MYSQL_PASSWORD', 'testpass'),
        'mysqlDB': os.getenv('MYSQL_DB', 'dev_db'),
        'mongoHost': os.getenv('MONGO_HOST', 'localhost'),
        'mongoUser': os.getenv('MONGO_USER', 'root'),
        'mongoPassword': os.getenv('MONGO_PASSWORD', 'testpass'),
        'mongoDB': os.getenv('MONGO_DB', 'silver-surfer'),
    }
    if os.getenv('FLASK_CONFIGURATION') == 'production':
        result = _get_ssm_parameters()
    return result


def _get_mysql_uri():
    environment = os.getenv('FLASK_CONFIGURATION')
    if environment == 'testing' or environment == 'ci':
        return 'sqlite://'

    credentials = _get_credentials()
    return 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
        credentials['mysqlUser'],
        credentials['mysqlPassword'],
        credentials['mysqlHost'],
        credentials['mysqlDB'],
    )


def _get_mongo_db_uri_and_db_name():
    credentials = _get_credentials()
    db_name = credentials['mongoDB']
    db_uri = 'mongodb+srv://{}:{}@{}/{}?retryWrites=true'.format(
        credentials['mongoUser'],
        credentials['mongoPassword'],
        credentials['mongoHost'],
        db_name,
    )
    return db_uri, db_name


def import_models():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # this usually happens when a model declares a FK constraint but the
    # referenced table hasn't been created yet
    import src.silver_surfer_models.resources.all_models  # noqa


mysql_db_uri = _get_mysql_uri()
engine = create_engine(
    mysql_db_uri,
    convert_unicode=True,
)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    ),
)

Base = declarative_base()
Base.query = db_session.query_property()


def get_mongo_db_session():
    mongo_db_uri, mongo_db_name = _get_mongo_db_uri_and_db_name()
    mongo_client = MongoClient(mongo_db_uri)
    mongo_db_session = mongo_client[mongo_db_name]
    return mongo_db_session
