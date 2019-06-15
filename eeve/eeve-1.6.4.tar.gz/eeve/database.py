from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    login = Column('login', String, nullable=False)
    password = Column('password', String, nullable=False)

    events = relationship('Event', backref=backref('users'), secondary='userHasEvent')


class Event(Base):
    __tablename__ = 'events'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    enabled = Column('enabled', Boolean, nullable=False, default=True)
    task_id = Column('task_id', Integer, ForeignKey('tasks.id'), unique=True)

    task = relationship("Task", backref=backref('event'), uselist=False)


class UserHasEvent(Base):
    __tablename__ = 'userHasEvent'
    event_id = Column('event_id', Integer, ForeignKey('events.id'), primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column('id', Integer, primary_key=True)
    #event_id = Column('event_id', Integer, ForeignKey('events.id'))
    # backref already defined in Event


class Action(Base):
    __tablename__ = 'actions'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)
    task_id = Column('task_id', Integer, ForeignKey('tasks.id'))

    task = relationship("Task", backref=backref('actions'))


class ActionArgument(Base):
    __tablename__ = 'actionArguments'
    id = Column('id', Integer, primary_key=True)
    key = Column('key', String)
    value = Column('value', String)
    action_id = Column('action_id', Integer, ForeignKey('actions.id'))

    action = relationship("Action", backref=backref('arguments'))


class Trigger(Base):
    __tablename__ = 'triggers'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)
    event_id = Column('event_id', Integer, ForeignKey('events.id'))

    event = relationship("Event", backref=backref('triggers'))


class TriggerArgument(Base):
    __tablename__ = 'triggerArguments'
    id = Column('id', Integer, primary_key=True)
    key = Column('key', String)
    value = Column('value', String)
    trigger_id = Column('trigger_id', Integer, ForeignKey('triggers.id'))

    trigger = relationship("Trigger", backref=backref('arguments'))


engine = Session = None


def open_db_file(path: str):
    global engine, Session
    if path:
        engine = create_engine(f'sqlite:///{path}', echo=True)
    else:
        engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)


def add_default_event():
    session = Session()

    event1 = Event(name='Default event',
                   users=[User(login='root', password='toor')],
                   triggers=[Trigger(name='on eeve startup')],
                   task=Task(actions=[Action(name='start gui')]))
    session.add(event1)
    session.commit()
    session.close()


def check_credentials(user_name: str, password: str) -> bool:
    try:
        print(user_name, password)
        session = Session()
        u = session.query(User).filter(User.login == user_name).filter(User.password == password).one()
        session.close()
        print(u)
        if u:
            print('deu bom')
            return True
        else:
            print('deu ruim')
            return False
    except:
        print('exceção')
        return False