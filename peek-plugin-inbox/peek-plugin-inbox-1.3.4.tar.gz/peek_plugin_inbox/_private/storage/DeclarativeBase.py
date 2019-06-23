
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData

metadata = MetaData(schema="pl_inbox")
DeclarativeBase = declarative_base(metadata=metadata)


def loadStorageTuples():
    from . import Task
    Task.__unused = False

    from . import TaskAction
    TaskAction.__unused = False

    from . import Activity
    Activity.__unused = False

    from . import Setting
    Setting.__unused = False
