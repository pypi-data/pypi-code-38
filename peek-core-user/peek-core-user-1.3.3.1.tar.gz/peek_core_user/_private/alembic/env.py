from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_core_user._private.storage import DeclarativeBase
from peek_core_user._private.storage.DeclarativeBase import loadStorageTuples

loadStorageTuples()


alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
