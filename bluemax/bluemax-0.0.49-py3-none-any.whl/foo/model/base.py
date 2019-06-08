''' Used by alembic '''
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=Base)
