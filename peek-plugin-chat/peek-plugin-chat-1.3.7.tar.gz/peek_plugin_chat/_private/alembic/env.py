from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_plugin_chat._private.storage import DeclarativeBase, loadStorageTuples

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.DeclarativeBase.metadata)
alembicEnv.run()