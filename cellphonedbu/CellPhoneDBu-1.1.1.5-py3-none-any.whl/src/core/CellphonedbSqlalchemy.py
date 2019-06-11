import os

from cellphonedb.src.core.Cellphonedb import Cellphonedb
from cellphonedb.src.core.core_logger import core_logger

class CellphonedbSqlalchemy(Cellphonedb):
    def __init__(self, config: dict):
        core_logger.setLevel(config['logger']['level'])

        Cellphonedb.__init__(self, config)

