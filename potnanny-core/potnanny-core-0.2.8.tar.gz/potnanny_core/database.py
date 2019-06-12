import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, create_session
from sqlalchemy.ext.declarative import declarative_base


engine = None
db_session = scoped_session(lambda: create_session(bind=engine,
                                                    autocommit=False,
                                                    autoflush=False,))

Base = declarative_base()
Base.query = db_session.query_property()


def init_engine(uri, **kwargs):
    """Initialize SQLAlchemy database engine."""

    global engine
    engine = create_engine(uri, **kwargs)


def init_db():
    """Initialize database tables."""

    from .models.measurement import Measurement
    from .models.sensor import Sensor
    from .models.room import Room
    from .models.grow import Grow
    from .models.trigger import Trigger
    from .models.outlet import Outlet
    from .models.schedule import ScheduleOnOff
    from .models.action import Action, SingularAction
    from .models.user import User
    from .models.keychain import Keychain

    Base.metadata.create_all(bind=engine)


def init_users():
    """Initialize default users."""

    from .models.user import User

    # build default user accounts
    for name in ['admin', 'potnanny']:
        u = User.query.filter_by(username=name).first()
        if not u:
            if name == 'admin':
                # default password = ?
                pw = '$pbkdf2-sha256$200000$DaH03rt37l1LaS1FKAVAqA$zMHfRyWe5/e1JD8gSL6OIhK6de5tYKzjnLrDPNaXMD8'
            else:
                # default password = 'potnanny'
                pw = '$pbkdf2-sha256$200000$xjiHsPZ.L.UcAwDg/N87pw$F.9uTLUWfmF8VRJ3CvpFK1Pm3xBwRJ.YYwmnpaQWE/k'

            u = User(
                username=name,
                password=pw,
            )
            db_session.add(u)
            db_session.commit()
