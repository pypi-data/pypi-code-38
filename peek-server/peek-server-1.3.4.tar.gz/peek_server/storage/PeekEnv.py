import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from peek_server.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class PeekEnvServer(Tuple, DeclarativeBase):
    """ PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server.env.server'
    __tablename__ = 'PeekEnvServer'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    workers = relationship("PeekEnvWorker")
    agent = relationship("PeekEnvAgent")


@addTupleType
class PeekEnvWorker(Tuple, DeclarativeBase):
    """ PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server.env.worker'
    __tablename__ = 'PeekEnvWorker'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(ForeignKey('peek_server.PeekEnvServer.id'), primary_key=True)
    server = relationship("PeekEnvServer")


@addTupleType
class PeekEnvAgent(Tuple, DeclarativeBase):
    """ PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server.env.agent'
    __tablename__ = 'PeekEnvAgent'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(ForeignKey('peek_server.PeekEnvServer.id'), primary_key=True)
    server = relationship("PeekEnvServer")


@addTupleType
class PeekEnvClient(Tuple, DeclarativeBase):
    """ PeekPluginInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server.env.client'
    __tablename__ = 'PeekEnvClient'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String(40), nullable=True, unique=True)

    serverId = Column(ForeignKey('peek_server.PeekEnvServer.id'), primary_key=True)
    server = relationship("PeekEnvServer")
