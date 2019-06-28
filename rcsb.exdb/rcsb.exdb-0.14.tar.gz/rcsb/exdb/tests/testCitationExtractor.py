##
# File:    CitationExtractorTests.py
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
import time
import unittest


from rcsb.exdb.citation.CitationExtractor import CitationExtractor
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class CitationExtractorTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(CitationExtractorTests, self).__init__(methodName)
        self.__verbose = True

    def setUp(self):
        #
        #
        self.__mockTopPath = os.path.join(TOPDIR, "rcsb", "mock-data")
        configPath = os.path.join(TOPDIR, "rcsb", "mock-data", "config", "dbload-setup-example.yml")
        #
        # Caution: this is very site specific setting !
        configName = "site_info_remote"
        self.__cfgOb = ConfigUtil(configPath=configPath, defaultSectionName=configName, mockTopPath=self.__mockTopPath)
        if configName != "site_info":
            self.__cfgOb.replaceSectionName("site_info", configName)
        #
        self.__workPath = os.path.join(HERE, "test-output")
        #
        self.__testCitationCacheKwargs = {"fmt": "json", "indent": 3}
        self.__testCitationCachePath = os.path.join(self.__workPath, "entry-citation-data-test-cache.json")
        #
        self.__mU = MarshalUtil()
        self.__entryLimitTest = 18
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)\n", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testExtractEntryCitations(self):
        """ Test case - extract entry citations

        """
        try:
            ce = CitationExtractor(
                self.__cfgOb, saveCachePath=self.__testCitationCachePath, useCache=True, saveCacheKwargs=self.__testCitationCacheKwargs, entryLimit=self.__entryLimitTest
            )
            eCount = ce.getEntryCount()
            self.assertGreaterEqual(eCount, self.__entryLimitTest)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def citationExtractorSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(CitationExtractorTests("testExtractEntryCitations"))

    return suiteSelect


if __name__ == "__main__":
    mySuite = citationExtractorSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
