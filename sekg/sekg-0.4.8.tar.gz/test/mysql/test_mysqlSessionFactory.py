from unittest import TestCase

from sekg.mysql.factory import MysqlSessionFactory


class TestMysqlSessionFactory(TestCase):
    def test_create_mysql_engine_by_server_name(self):
        factory = MysqlSessionFactory("mysql_config.json")

        engine = factory.create_mysql_engine_by_server_name("87RootServer")
        self.assertIsNotNone(engine)

        engine = factory.create_mysql_engine_by_server_name("DysD3Wrong")
        self.assertIsNone(engine)

    def test_create_mysql_engine_by_server_id(self):
        factory = MysqlSessionFactory("mysql_config.json")
        engine = factory.create_mysql_engine_by_server_id(1)
        self.assertIsNotNone(engine)

        engine3 = factory.create_mysql_engine_by_server_id(3)
        self.assertIsNone(engine3)

    def test_create_mysql_session_by_server_name(self):
        factory = MysqlSessionFactory("mysql_config.json")

        session = factory.create_mysql_session_by_server_name("87RootServer", database="testsekg")
        self.assertIsNotNone(session)

        session = factory.create_mysql_session_by_server_name("DysD3Wrong", database="testsekg")
        self.assertIsNone(session)

    def test_create_mysql_session_by_server_id(self):
        factory = MysqlSessionFactory("mysql_config.json")
        session = factory.create_mysql_session_by_server_id(1, database="testsekg")
        self.assertIsNotNone(session)

        engine3 = factory.create_mysql_session_by_server_id(3, database="testsekg")
        self.assertIsNone(engine3)

    def test_create_all_databases(self):
        factory = MysqlSessionFactory("mysql_config.json")
        factory.create_all_databases(server_name="87RootServer")
