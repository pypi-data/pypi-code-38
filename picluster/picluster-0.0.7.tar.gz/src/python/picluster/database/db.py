from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import contextlib

from ..config.base import DBConfig
from .model.schema import meta


class DataBase:
    def __init__(
        self,
        ip: str = DBConfig.DB_IP,
        user: str = DBConfig.DB_USER,
        passwd: str = DBConfig.DB_PASSWD,
        database: str = DBConfig.DB_NAME,
        port: str = DBConfig.DB_PORT,
    ):
        self.user = user
        self.passwd = passwd
        self.database = database
        self.ip = ip
        self.port = port
        self.maker = None
        self.engine = None

    def __repr__(self):
        return f"{self.__class__.__name__}(database={self.database}, ip={self.ip}, port={self.port}, user={self.user})"

    def get_or_create_engine(self):
        if self.engine is not None:
            return self.engine

        elif self.engine is None:
            self.engine = create_engine(
                f"postgresql://{self.user}:{self.passwd}@{self.ip}:{self.port}/{self.database}"
            )
            return self.engine

    def get_or_create_maker(self):
        if self.maker is None:
            self.maker = sessionmaker(self.get_or_create_engine())
        return self.maker

    @contextlib.contextmanager
    def session(self):
        sess = self.get_or_create_maker()()
        try:
            yield sess
        except Exception as e:
            sess.rollback()
            raise e
        finally:
            sess.close()

    def create_all(self):
        return meta.create_all(self.get_or_create_engine())

    def drop_all(self):
        return meta.drop_all(self.get_or_create_engine())
