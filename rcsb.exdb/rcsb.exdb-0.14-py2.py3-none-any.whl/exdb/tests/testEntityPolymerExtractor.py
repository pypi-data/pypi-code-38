##
# File:    EntityPolymerExtractorTests.py
# Author:  J. Westbrook
# Date:    25-Mar-2019
#
# Updates:
#  21-Apr-2019 jdw Separate tests against the  mock-data repo in this module
#
##
"""
Tests for extractor entity polymer instance collections (limited tests from mock-data repos)

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging
import os
import time
import unittest


from rcsb.exdb.seq.EntityPolymerExtractor import EntityPolymerExtractor
from rcsb.utils.config.ConfigUtil import ConfigUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil

from rcsb.utils.taxonomy.TaxonomyUtils import TaxonomyUtils

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


class EntityPolymerExtractorTests(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(EntityPolymerExtractorTests, self).__init__(methodName)
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
        self.__testEntityPolymerCacheKwargs = {"fmt": "json", "indent": 3}
        self.__testEntityPolymerCachePath = os.path.join(self.__workPath, "entity-polymer-data-test-cache.json")
        #
        self.__mU = MarshalUtil()
        self.__entryLimitTest = 18
        #
        self.__startTime = time.time()
        logger.debug("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)\n", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testExtractEntityPolymers(self):
        """ Test case - extract entity polymer info

        """
        try:
            epe = EntityPolymerExtractor(
                self.__cfgOb, saveCachePath=self.__testEntityPolymerCachePath, useCache=False, saveCacheKwargs=self.__testEntityPolymerCacheKwargs, entryLimit=self.__entryLimitTest
            )
            eCount = epe.getEntryCount()
            self.assertGreaterEqual(eCount, self.__entryLimitTest)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testAccessEntityPolymerFeatures(self):
        """ Test case - access cached entity polymer info from test cache

        """
        try:
            epe = EntityPolymerExtractor(self.__cfgOb, saveCachePath=self.__testEntityPolymerCachePath, useCache=False, saveCacheKwargs=self.__testEntityPolymerCacheKwargs)
            eCount = epe.getEntryCount()
            logger.info("Entry count %d", eCount)
            self.assertGreaterEqual(eCount, self.__entryLimitTest)
            #
            unpL = epe.getRefSeqAccessions("UNP")
            logger.info("Ref seq count %d", len(unpL))
            self.assertGreaterEqual(len(unpL), 1)
            #
            for entryId in ["3RER"]:
                for entityId in ["1"]:
                    uL = epe.getEntityRefSeqAccessions("UNP", entryId, entityId)
                    logger.info("UNP for %s %s %r", entryId, entityId, uL)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testTaxonomyReadCache(self):
        """ Test case - access cached entity polymer info from test cache

        """
        try:
            epe = EntityPolymerExtractor(self.__cfgOb, saveCachePath=self.__testEntityPolymerCachePath, useCache=False, saveCacheKwargs=self.__testEntityPolymerCacheKwargs)
            logger.info("Cache entry count %d", epe.getEntryCount())
            #
            obsL = []
            tD = epe.getOrigTaxons()
            logger.info("Taxons %d", len(tD))
            tU = TaxonomyUtils(taxDirPath=self.__workPath)
            for entryId, taxIdL in tD.items():
                for entityId, iTaxId in taxIdL:
                    # logger.info("entryId %r entityId %r taxId %r" % (entryId, entityId, taxId))
                    mTaxId = tU.getMergedTaxId(iTaxId)
                    if iTaxId != mTaxId:
                        obsL.append({"entryId": entryId, "entityId": entityId, "taxId": iTaxId, "replaceTaxId": mTaxId})
            logger.info("Obsolete list length %d", len(obsL))
            self.__mU.doExport(os.path.join(self.__workPath, "obsolete-taxons.json"), obsL, fmt="json", indent=3)
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testAccessEntityPolymerReadCache(self):
        """ Test case - access cached entity polymer info from test cache

        """
        try:
            epe = EntityPolymerExtractor(self.__cfgOb, saveCachePath=self.__testEntityPolymerCachePath, useCache=False, saveCacheKwargs=self.__testEntityPolymerCacheKwargs)
            logger.info("Cache entry count %d", epe.getEntryCount())
            cD = epe.countRefSeqAccessions("UNP")
            self.assertGreaterEqual(len(cD), 2)
            logger.info("UNP reference sequences per entity %r", dict(sorted(cD.items())))
            logger.info("Reference sequences per entity %r", dict(sorted(epe.countRefSeqAccessionAny().items())))
            logger.info("Reference sequences per ref db %r", dict(sorted(epe.countRefSeqAccessionDbType().items())))
            #
            ok = epe.checkRefSeqAlignRange("UNP")
            self.assertTrue(ok)
            unpL = epe.getRefSeqAccessions("UNP")
            logger.info("Unique UNP reference sequences %d", len(unpL))
            self.assertTrue(ok)
            tD = epe.getUniqueTaxons()
            logger.info("Unique taxons %d", len(tD))
            tD = epe.countRefSeqAccessionByTaxon("UNP")
            logger.info("Unique taxons %d", len(tD))
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def entityPolymerExtractSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(EntityPolymerExtractorTests("testExtractEntityPolymers"))
    suiteSelect.addTest(EntityPolymerExtractorTests("testAccessEntityPolymerFeatures"))
    suiteSelect.addTest(EntityPolymerExtractorTests("testAccessEntityPolymerReadCache"))
    return suiteSelect


def entityTaxonomyExtractSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(EntityPolymerExtractorTests("testTaxonomyReadCache"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = entityPolymerExtractSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)

    mySuite = entityTaxonomyExtractSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
