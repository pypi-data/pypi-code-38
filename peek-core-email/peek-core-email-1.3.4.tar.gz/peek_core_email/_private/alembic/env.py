from peek_core_email._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_core_email._private.storage import DeclarativeBase

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
