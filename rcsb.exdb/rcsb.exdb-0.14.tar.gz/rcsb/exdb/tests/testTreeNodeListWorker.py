##
# File:    TreeNodeListWorkerTests.py
# Author:  J. Westbrook
# Date:    23-Apr-2019
#
# Updates:
#
##
"""
Tests for for tree node list worker ---

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import time
import unittest

from rcsb.db.utils.TimeUtil import TimeUtil
from rcsb.exdb.cli.TreeNodeListWorker import TreeNodeListWorker

from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class TreeNodeListWorkerTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(TreeNodeListWorkerTests, self).__init__(methodName)
        self.__verbose = True

    def setUp(self):
        #
        #
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        configPath = os.path.join(TOPDIR, "rcsb", "mock-data", "config", "dbload-setup-example.yml")
        #
        # Caution: this is very site specific setting !
        configName = "site_info"
        self.__cfgOb = ConfigUtil(configPath=configPath, defaultSectionName=configName, mockTopPath=self.__mockTopPath)
        if configName != "site_info":
            self.__cfgOb.replaceSectionName("site_info", configName)
        #
        self.__topCachePath = self.__mockTopPath
        #
        self.__mU = MarshalUtil()
        #
        self.__readBackCheck = True
        self.__numProc = 2
        self.__chunkSize = 10
        self.__documentLimit = None
        self.__debugFlag = False
        self.__loadType = "full"
        self.__useCache = True
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)\n", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testTreeLoader(self):
        """ Test case - extract entity polymer info

        """
        try:
            tU = TimeUtil()
            updateId = tU.getCurrentWeekSignature()
            rhw = TreeNodeListWorker(
                self.__cfgOb,
                mockTopPath=self.__mockTopPath,
                numProc=self.__numProc,
                chunkSize=self.__chunkSize,
                documentLimit=self.__documentLimit,
                verbose=self.__debugFlag,
                readBackCheck=self.__readBackCheck,
                topCachePath=self.__topCachePath,
                useCache=self.__useCache,
            )
            #
            ok = rhw.load(updateId, loadType=self.__loadType)
            self.assertTrue(ok)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def treeNodeListSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(TreeNodeListWorkerTests("testTreeLoader"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = treeNodeListSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
