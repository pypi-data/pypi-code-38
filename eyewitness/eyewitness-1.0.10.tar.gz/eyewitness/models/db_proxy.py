from peewee import Proxy

# Using Peewee proxy to dynamically define database in runtime
# http://docs.peewee-orm.com/en/latest/peewee/database.html#dynamically-defining-a-database
DATABASE_PROXY = Proxy()
