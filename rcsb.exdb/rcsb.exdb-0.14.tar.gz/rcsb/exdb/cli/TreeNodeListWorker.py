##
# File: TreeNodeListWorker.py
# Date: 9-Apr-2019  jdw
#
# Loading worker for tree node list data.
#
# Updates:
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import glob
import logging
import os.path

from rcsb.db.mongo.DocumentLoader import DocumentLoader
from rcsb.db.processors.DataExchangeStatus import DataExchangeStatus
from rcsb.exdb.seq.EntityPolymerExtractor import EntityPolymerExtractor
from rcsb.utils.ec.EnzymeDatabaseUtils import EnzymeDatabaseUtils
from rcsb.utils.struct.CathClassificationUtils import CathClassificationUtils
from rcsb.utils.struct.ScopClassificationUtils import ScopClassificationUtils
from rcsb.utils.taxonomy.TaxonomyUtils import TaxonomyUtils

logger = logging.getLogger(__name__)


class TreeNodeListWorker(object):
    """ Prepare and load repository holdings and repository update data.
    """

    def __init__(self, cfgOb, mockTopPath, topCachePath=None, numProc=1, chunkSize=10, readBackCheck=False, documentLimit=None, verbose=False, useCache=False):
        self.__cfgOb = cfgOb
        self.__mockTopPath = mockTopPath
        self.__topCachePath = os.path.abspath(topCachePath)
        self.__readBackCheck = readBackCheck
        self.__numProc = numProc
        self.__chunkSize = chunkSize
        self.__documentLimit = documentLimit
        self.__resourceName = "MONGO_DB"
        self.__filterType = "assign-dates"
        self.__verbose = verbose
        self.__statusList = []
        self.__useCache = useCache

    def __updateStatus(self, updateId, databaseName, collectionName, status, startTimestamp):
        try:
            sFlag = "Y" if status else "N"
            desp = DataExchangeStatus()
            desp.setStartTime(tS=startTimestamp)
            desp.setObject(databaseName, collectionName)
            desp.setStatus(updateId=updateId, successFlag=sFlag)
            desp.setEndTime()
            self.__statusList.append(desp.getStatus())
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def load(self, updateId, loadType="full"):
        """ Load tree node lists and status data -

        Relevant configuration options:

        tree_node_lists:
            DATABASE_NAME: tree_node_lists
            DATABASE_VERSION_STRING: v5
            COLLECTION_VERSION_STRING: 1.0.0
            COLLECTION_TAXONOMY: tree_taxonomy_node_list
            COLLECTION_ENZYME: tree_ec_node_list
            COLLECTION_SCOP: tree_scop_node_list
            COLLECTION_CATH: tree_cath_node_list

        """
        try:
            useCache = self.__useCache
            topCachePath = self.__topCachePath
            #
            if not useCache:
                cDL = ["domains_struct", "NCBI", "ec", "exdb"]
                for cD in cDL:
                    try:
                        cfp = os.path.join(topCachePath, cD)
                        os.makedirs(cfp, 0o755)
                    except Exception:
                        pass
                    #
                    try:
                        cfp = os.path.join(topCachePath, cD)
                        fpL = glob.glob(os.path.join(cfp, "*"))
                        if fpL:
                            for fp in fpL:
                                os.remove(fp)
                    except Exception:
                        pass
            #
            logger.info("Using cache files in %s %r", topCachePath, useCache)
            #
            sectionName = "tree_node_lists"
            #
            self.__statusList = []
            desp = DataExchangeStatus()
            statusStartTimestamp = desp.setStartTime()
            # ------------------ -------------- -------------- -------------- -------------- --------------
            #

            dl = DocumentLoader(
                self.__cfgOb,
                self.__resourceName,
                numProc=self.__numProc,
                chunkSize=self.__chunkSize,
                documentLimit=self.__documentLimit,
                verbose=self.__verbose,
                readBackCheck=self.__readBackCheck,
            )
            #
            databaseName = self.__cfgOb.get("DATABASE_NAME", sectionName=sectionName)
            collectionVersion = self.__cfgOb.get("COLLECTION_VERSION_STRING", sectionName=sectionName)
            addValues = {"_schema_version": collectionVersion}
            #
            #
            ccu = CathClassificationUtils(cathDirPath=os.path.join(topCachePath, "domains_struct"), useCache=useCache)
            nL = ccu.getTreeNodeList()
            logger.info("Starting load SCOP node tree %d", len(nL))
            collectionName = self.__cfgOb.get("COLLECTION_CATH", sectionName=sectionName)
            ok = dl.load(databaseName, collectionName, loadType=loadType, documentList=nL, indexAttributeList=["update_id"], keyNames=None, addValues=addValues)
            self.__updateStatus(updateId, databaseName, collectionName, ok, statusStartTimestamp)

            scu = ScopClassificationUtils(scopDirPath=os.path.join(topCachePath, "domains_struct"), useCache=useCache)
            nL = scu.getTreeNodeList()
            logger.info("Starting load SCOP node tree %d", len(nL))
            collectionName = self.__cfgOb.get("COLLECTION_SCOP", sectionName=sectionName)
            ok = dl.load(databaseName, collectionName, loadType=loadType, documentList=nL, indexAttributeList=["update_id"], keyNames=None, addValues=addValues)
            self.__updateStatus(updateId, databaseName, collectionName, ok, statusStartTimestamp)

            edbu = EnzymeDatabaseUtils(enzymeDirPath=os.path.join(topCachePath, "ec"), useCache=useCache, clearCache=False)
            nL = edbu.getTreeNodeList()
            logger.info("Starting load EC node tree %d", len(nL))
            collectionName = self.__cfgOb.get("COLLECTION_ENZYME", sectionName=sectionName)
            ok = dl.load(databaseName, collectionName, loadType=loadType, documentList=nL, indexAttributeList=["update_id"], keyNames=None, addValues=addValues)
            self.__updateStatus(updateId, databaseName, collectionName, ok, statusStartTimestamp)

            # Get the taxon coverage in the current data set -
            cacheKwargs = {"fmt": "pickle"}
            epe = EntityPolymerExtractor(
                self.__cfgOb, saveCachePath=os.path.join(topCachePath, "exdb", "entity-polymer-data-cache.pic"), useCache=useCache, saveCacheKwargs=cacheKwargs
            )
            logger.info("Entity polymer cache entry count %d", epe.getEntryCount())
            tD = epe.getUniqueTaxons()
            logger.info("Taxon coverage length %d", len(tD))
            #
            tU = TaxonomyUtils(taxDirPath=os.path.join(topCachePath, "NCBI"), useCache=useCache)
            fD = {1}
            for taxId in tD:
                fD.update({k: True for k in tU.getLineage(taxId)})
            logger.info("Filter taxon dictionary length %d", len(fD))
            # logger.info("fD %r" % sorted(fD))
            #
            nL = tU.exportNodeList(filterD=fD)
            self.__checkTaxonNodeList(nL)

            logger.info("Starting load taxonomy node tree %d", len(nL))
            collectionName = self.__cfgOb.get("COLLECTION_TAXONOMY", sectionName=sectionName)
            ok = dl.load(databaseName, collectionName, loadType=loadType, documentList=nL, indexAttributeList=["update_id"], keyNames=None, addValues=addValues)
            logger.info("Tree loading operations completed.")
            #
            # ------------------ -------------- -------------- -------------- -------------- --------------
            self.__updateStatus(updateId, databaseName, collectionName, ok, statusStartTimestamp)

            #
            return True
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return False

    def __checkTaxonNodeList(self, nL):
        eCount = 0
        tD = {dD["id"]: True for dD in nL}
        for dD in nL:
            if "parents" in dD:
                pId = dD["parents"][0]
                if pId not in tD:
                    logger.info("Missing parent for taxon %d", pId)
                    eCount += 1
            else:
                logger.info("No parents for node %r", dD["id"])

    def getLoadStatus(self):
        return self.__statusList
