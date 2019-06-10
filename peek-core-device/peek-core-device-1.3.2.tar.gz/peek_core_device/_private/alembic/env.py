from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_core_device._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_device._private.storage import DeclarativeBase

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.DeclarativeBase.metadata)
alembicEnv.run()