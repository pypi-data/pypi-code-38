from unittest import TestCase

from sqlalchemy import Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base

from sekg.mysql.accessor import MySQLAccessor
from sekg.mysql.factory import MysqlSessionFactory

Base = declarative_base()


class APIModel(Base):
    __tablename__ = 'api_test_model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=True)

    def __init__(self, name):
        self.name = name


class TestMySQLAccessor(TestCase):
    def test_delete_all(self):
        factory = MysqlSessionFactory("mysql_config.json")
        engine = factory.create_mysql_engine_by_server_id(1, database="testsekg")
        mysql_accessor = MySQLAccessor(engine=engine)
        mysql_accessor.create_orm_tables(SqlachemyORMBaseClass=Base)
        mysql_accessor.delete_all(APIModel)

    def test_create_table(self):
        factory = MysqlSessionFactory("mysql_config.json")
        engine = factory.create_mysql_engine_by_server_id(1, database="test", echo=True)
        mysql_accessor = MySQLAccessor(engine=engine)
        mysql_accessor.create_orm_tables(SqlachemyORMBaseClass=Base)
        mysql_accessor.drop_orm_tables(SqlachemyORMBaseClass=Base)

    def test_get_by_primary_key(self):
        factory = MysqlSessionFactory("mysql_config.json")
        engine = factory.create_mysql_engine_by_server_id(1, database="test", echo=True)
        mysql_accessor = MySQLAccessor(engine=engine)
        mysql_accessor.create_orm_tables(SqlachemyORMBaseClass=Base)

        api = mysql_accessor.get_by_primary_key(model_class=APIModel, primary_property=APIModel.id,
                                                primary_property_value=3)
        self.assertIsNone(api)
        # todo, add method for more
