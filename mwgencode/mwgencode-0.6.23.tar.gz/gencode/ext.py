from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# class Base(Model):
#     # # create_at这个属性也是创建表结构默认都包含的
#     # create_at = Column(DateTime, default=datetime.utcnow())
#     def to_json(self):
#         columns = self.__table__.columns.keys()
#         return {key: getattr(self, key) for key in columns}

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)

def new_id():
    from datetime import datetime
    return datetime.today().strftime("%Y%m%d%H%M%S%f")