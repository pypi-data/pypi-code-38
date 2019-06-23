"""
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""

import logging
from typing import Dict

from sqlalchemy import MetaData

from peek_plugin_base.storage.DbConnection import DbConnection

logger = logging.getLogger(__name__)

dbConn = None


def setupDbConn(dbConnectString: str, metadata: MetaData, alembicDir: str,
                dbEngineArgs: Dict):
    global dbConn
    dbConn = DbConnection(dbConnectString=dbConnectString,
                          metadata=metadata,
                          alembicDir=alembicDir,
                          dbEngineArgs=dbEngineArgs,
                          enableCreateAll=False,
                          enableForeignKeys=False)


from . import PeekPluginInfo
from . import Setting
from . import PeekEnv
