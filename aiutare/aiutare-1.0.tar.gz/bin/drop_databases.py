from mongoengine import connect


from bin.config import config

db1 = connect(config["database_name"])
db1.drop_database(config["database_name"])
