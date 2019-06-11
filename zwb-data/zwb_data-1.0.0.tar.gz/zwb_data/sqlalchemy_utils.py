from contextlib import contextmanager
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class DbClient:

    def __init__(self, *args, **kwargs):
        self.engine = create_engine(*args, **kwargs)
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()

    def open_session(self):
        return self.Session()

    @contextmanager
    def open_session_scope(self):
        session = self.open_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def init(self):
        self.Base.metadata.create_all(engine)


if __name__ == "__main__":
    db = DbClient("mysql+mysqlconnector://root:root@192.168.19.11/demo")

    class User(db.Base):
        __tablename__ = 'user'
        id = Column(String(20), primary_key=True)
        name = Column(String(20))

    with db.open_session_scope() as session:
        user = User()
        user.id = "44"
        user.name = "dd"
        session.add(user)
