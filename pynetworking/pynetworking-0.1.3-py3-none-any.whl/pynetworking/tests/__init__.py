import sys
import os
project_path = os.path.abspath(__file__ + "../../../..")
sys.path.insert(0, project_path)

from pynetworking.Logging import logger
logger.setLevel(30)

