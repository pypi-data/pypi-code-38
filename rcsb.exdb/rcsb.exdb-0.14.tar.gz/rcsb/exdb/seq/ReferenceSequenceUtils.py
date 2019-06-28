##
# File: ReferenceSequenceUtils.py
# Date: 28-Mar-2019  jdw
#
# Selected utilities to integrate reference sequence information with PDB polymer entity data.
#
# Updates:
#  21-Apr-2019 jdw refactor
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging

from rcsb.exdb.seq.EntityPolymerExtractor import EntityPolymerExtractor
from rcsb.utils.io.MarshalUtil import MarshalUtil
from rcsb.utils.seq.UniProtUtils import UniProtUtils

logger = logging.getLogger(__name__)


class ReferenceSequenceUtils(object):
    """  Selected utilities to integrate reference sequence information with PDB polymer entity data.

    """

    def __init__(self, cfgOb, refDbName, **kwargs):
        self.__cfgOb = cfgOb
        self.__refDbName = refDbName
        self.__mU = MarshalUtil()
        #
        self.__refIdList = self.__getReferenceAssignments(refDbName, **kwargs)
        self.__refD, self.__matchD = self.__rebuildCache(refDbName, self.__refIdList, **kwargs)

    def __getReferenceAssignments(self, refDbName, **kwargs):
        """ Get all accessions assigned to input reference sequence database

        """
        rL = []
        entityCachePath = kwargs.get("entityPolymerCachePath", None)
        entityCacheKwargs = kwargs.get("entityPolymerCacheKwargs", None)
        useCache = kwargs.get("useEntityPolymerCache", True)
        entryLimit = kwargs.get("entryLimit", None)

        try:
            epe = EntityPolymerExtractor(self.__cfgOb, saveCachePath=entityCachePath, useCache=useCache, saveCacheKwargs=entityCacheKwargs, entryLimit=entryLimit)
            eCount = epe.getEntryCount()
            rL = epe.getRefSeqAccessions(refDbName)
            logger.info("Reading polymer entity cache with PDB entry count %d ref accession length %d ", eCount, len(rL))
            #
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return rL

    def __rebuildCache(self, refDbName, idList, **kwargs):
        """
        """
        dD = {}
        refCachePath = kwargs.get("referenceCachePath", None)
        refCacheKwargs = kwargs.get("referenceCacheKwargs", None)
        useCache = kwargs.get("useReferenceCache", True)
        fetchLimit = kwargs.get("fetchLimit", None)
        #
        if useCache and refCachePath and self.__mU.exists(refCachePath):
            dD = self.__mU.doImport(refCachePath, **refCacheKwargs)
        else:
            dD = self.__fetchReferenceEntries(refDbName, idList, saveText=False, fetchLimit=fetchLimit)
            if refCachePath and refCacheKwargs:
                ok = self.__mU.doExport(refCachePath, dD, **refCacheKwargs)
                logger.info("Cache save status %r", ok)

        return dD["refDbCache"], dD["matchInfo"]

    def __fetchReferenceEntries(self, refDbName, idList, saveText=False, fetchLimit=None):
        """ Fetch database entries from the input reference sequence database name.
        """
        dD = {"refDbName": refDbName, "refDbCache": {}, "matchInfo": {}}

        try:
            idList = idList[:fetchLimit] if fetchLimit else idList
            logger.info("Starting fetch for %d %s entries", len(idList), refDbName)
            if refDbName == "UNP":
                fobj = UniProtUtils(saveText=saveText)
                refD, matchD = fobj.fetchList(idList)
                dD = {"refDbName": refDbName, "refDbCache": refD, "matchInfo": matchD}

        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return dD

    def __dumpEntries(self, refD):
        for (eId, eDict) in refD.items():
            logger.info("------ Entry id %s", eId)
            for k, v in eDict.items():
                logger.info("%-15s = %r", k, v)

    def getReferenceAccessionAlignSummary(self):
        """ Summarize the alignment of PDB accession assignments with the current reference sequence database.
        """
        numPrimary = 0
        numSecondary = 0
        numNone = 0
        for _, mD in self.__matchD.items():
            if mD["matched"] == "primary":
                numPrimary += 1
            elif mD["matched"] == "secondary":
                numSecondary += 1
            else:
                numNone += 1
        logger.debug("Matched primary:  %d secondary: %d none %d", numPrimary, numSecondary, numNone)
        return numPrimary, numSecondary, numNone
