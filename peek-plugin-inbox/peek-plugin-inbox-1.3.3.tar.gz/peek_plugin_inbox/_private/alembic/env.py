from peek_plugin_inbox._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_plugin_inbox._private.storage import DeclarativeBase

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
