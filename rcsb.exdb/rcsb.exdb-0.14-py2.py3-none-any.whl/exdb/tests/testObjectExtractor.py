##
# File:    ObjectExtractorTests.py
# Author:  J. Westbrook
# Date:    25-Apr-2019
#
# Updates:
#
##
"""
Tests for extractor selected values from collections (limited tests from mock-data repos)
"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import pprint
import time
import unittest


from rcsb.exdb.utils.ObjectExtractor import ObjectExtractor
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class ObjectExtractorTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(ObjectExtractorTests, self).__init__(methodName)
        self.__verbose = True

    def setUp(self):
        #
        #
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        configPath = os.path.join(TOPDIR, "rcsb", "mock-data", "config", "dbload-setup-example.yml")
        #
        # Caution: this is very site specific setting !
        configName = "site_info_remote"
        # configName = "site_info"
        self.__cfgOb = ConfigUtil(configPath=configPath, defaultSectionName=configName, mockTopPath=self.__mockTopPath)
        if configName != "site_info":
            self.__cfgOb.replaceSectionName("site_info", configName)
        #
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__testEntryCacheKwargs = {"fmt": "json", "indent": 3}
        # self.__testEntryCachePath = os.path.join(self.__workPath, "entry-data-test-cache.json")
        #
        self.__mU = MarshalUtil()
        self.__objectLimitTest = 5
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)\n", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testExtractEntries(self):
        """ Test case - extract entries

        """
        try:
            obEx = ObjectExtractor(
                self.__cfgOb,
                dbName="pdbx_core",
                collectionName="pdbx_core_entry",
                saveCachePath=os.path.join(self.__workPath, "entry-data-test-cache.json"),
                useCache=False,
                keyAttribute="entry",
                uniqueAttributes=["_entry_id"],
                saveCacheKwargs=self.__testEntryCacheKwargs,
                objectLimit=self.__objectLimitTest,
            )
            eCount = obEx.getCount()
            logger.info("Entry count is %d", eCount)
            self.assertGreaterEqual(eCount, self.__objectLimitTest)

            objD = obEx.getObjects()
            for _, obj in objD.items():
                # obEx.genPathList(obj["software"], path=["software"])
                obEx.genPathList(obj, path=None)

            #
            pL = obEx.getPathList(filterList=True)
            obEx.setPathList(pL)
            for ky, obj in objD.items():
                obEx.genValueList(obj, path=None)
                tD = obEx.getValues()
                logger.debug("Index object %r %s", ky, pprint.pformat(tD, indent=3, width=120))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testExtractEntities(self):
        """ Test case - extract entities

        """
        try:
            obEx = ObjectExtractor(
                self.__cfgOb,
                dbName="pdbx_core",
                collectionName="pdbx_core_entity",
                saveCachePath=os.path.join(self.__workPath, "entity-data-test-cache.json"),
                useCache=False,
                keyAttribute="entity",
                uniqueAttributes=["_entry_id", "_entity_id"],
                saveCacheKwargs=self.__testEntryCacheKwargs,
                objectLimit=self.__objectLimitTest,
            )
            eCount = obEx.getCount()
            logger.info("Entity count is %d", eCount)
            self.assertGreaterEqual(eCount, self.__objectLimitTest)

            objD = obEx.getObjects()
            for _, obj in objD.items():
                obEx.genPathList(obj, path=None)
            #
            pL = obEx.getPathList(filterList=False)
            logger.debug("Path list (unfiltered) %r", pL)
            #
            pL = obEx.getPathList()
            logger.debug("Path list %r", pL)
            obEx.setPathList(pL)
            for ky, obj in objD.items():
                obEx.genValueList(obj, path=None)
                tD = obEx.getValues()
                logger.debug("Index object %r %s", ky, pprint.pformat(tD, indent=3, width=120))

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def objectExtractorSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ObjectExtractorTests("testExtractEntries"))
    suiteSelect.addTest(ObjectExtractorTests("testExtractEntities"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = objectExtractorSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
