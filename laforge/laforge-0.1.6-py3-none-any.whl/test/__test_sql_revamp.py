import pandas as pd
import sqlalchemy as sa
from sqlalchemy import func

from bergholt import sql

# https://www.pythonsheets.com/notes/python-sqlalchemy.html

df = pd.DataFrame([[1], [2], [3]], columns=["bob"])

eng = sa.create_engine("sqlite:///")
md = sa.MetaData(eng)
eng2 = sa.create_engine(
    "postgresql+psycopg2://test_mason:test_mason@localhost/test_mason"
)
md2 = sa.MetaData(eng2)
eng3 = sa.create_engine(
    "postgresql+psycopg2://test_mason:test_mason@localhosf/test_mason"
)
md3 = sa.MetaData(eng3)

tab = sa.Table("hi", md)

df.to_sql(tab.name, con=tab.bind, schema=tab.schema)

tab = sa.Table("hi", md, autoload=True, autoload_with=eng, extend_existing=True)

print(
    {
        "db": eng2.url.database,
        "server": eng2.url.host,
        "driver": eng2.url.drivername,
        "distro": eng2.url.get_backend_name(),
    }
)

stmt = sa.select([tab])
print(stmt)
rp = print(eng2.execute(stmt))

df2 = pd.read_sql(stmt, con=eng2)
print(df)
print(df2)
# print(sa.inspect(eng).get_table_names())

# t_before.drop()
# print(t.exists())
# print(sa.inspect(eng).get_table_names())

# df.to_sql(t.name, con=t.bind, schema=t.schema)
# print(sa.inspect(eng).get_table_names())
# print(dir(t))

# t2 = sa.Table(t.name, md, autoload=True, autoload_with=eng)

# md.reflect(extend_existing=True, only=["hi"])
