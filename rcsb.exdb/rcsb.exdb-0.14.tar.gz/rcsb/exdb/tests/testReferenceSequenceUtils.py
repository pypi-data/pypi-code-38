##
# File:    ReferenceSequenceUtilsTests.py
# Author:  J. Westbrook
# Date:    25-Mar-2019
#
# Updates:
#
##
"""
Tests for accessing reference sequence data corresponding to polymer entity sequence assignments.

(Limited tests against to mock-data repos.)

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import time
import unittest


from rcsb.exdb.seq.ReferenceSequenceUtils import ReferenceSequenceUtils
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class ReferenceSequenceUtilsTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(ReferenceSequenceUtilsTests, self).__init__(methodName)
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
        self.__workPath = os.path.join(HERE, "test-output")
        #
        # Reference sequence test data cache -
        #
        self.__refDbCachePath = os.path.join(HERE, "test-output", "unp-data-test-cache.json")
        self.__refDbCacheKwargs = {"fmt": "json", "indent": 3}
        self.__refDbUseCache = True
        self.__fetchLimit = None
        #
        # Entity polymer extracted data ...
        #
        self.__testEntityPolymerCacheKwargs = {"fmt": "json", "indent": 3}
        self.__testEntityPolymerCachePath = os.path.join(self.__workPath, "entity-polymer-data-test-cache.json")
        self.__useEntityPolymerCache = True
        self.__entryLimit = 500
        #
        self.__mU = MarshalUtil()
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)\n", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testFetchUnp(self):
        """ Test case - extract entity polymer info -

        """
        try:
            refDbName = "UNP"
            rsu = ReferenceSequenceUtils(
                self.__cfgOb,
                refDbName,
                referenceCachePath=self.__refDbCachePath,
                referenceCacheKwargs=self.__refDbCacheKwargs,
                useReferenceCache=self.__refDbUseCache,
                entityPolymerCachePath=self.__testEntityPolymerCachePath,
                entityPolymerCacheKwargs=self.__testEntityPolymerCacheKwargs,
                useEntityPolymerCache=self.__useEntityPolymerCache,
                entryLimit=self.__entryLimit,
                fetchLimit=self.__fetchLimit,
            )
            numPrimary, numSecondary, numNone = rsu.getReferenceAccessionAlignSummary()
            self.assertGreaterEqual(numPrimary, 70)
            logger.info("For %r matched primary:  %d secondary: %d none %d", refDbName, numPrimary, numSecondary, numNone)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def unpFetchSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ReferenceSequenceUtilsTests("testFetchUnp"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = unpFetchSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
