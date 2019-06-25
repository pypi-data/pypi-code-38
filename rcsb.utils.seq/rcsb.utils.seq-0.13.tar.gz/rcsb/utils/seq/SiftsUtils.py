##
# File:    SiftsUtils.py
# Author:  J. Westbrook
# Date:    11-Dec-2018
#
# Updates:

##
"""
Utilities to access SIFTS summary mapping data.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class SiftsUtils(object):
    """

    """

    def __init__(self, **kwargs):
        self.__ssD = self.__rebuildCache(**kwargs)

    def getEntryCount(self):
        return len(self.__ssD)

    def getAlignmentCount(self, entryId, authAsymId):
        num = 0
        try:
            num = len(self.__ssD[entryId][authAsymId]["AL"])
        except Exception:
            pass
        return num

    def getAlignments(self, entryId, authAsymId):
        aL = []
        try:
            aL = self.__ssD[entryId][authAsymId]["AL"]
        except Exception:
            pass
        return aL

    def getTaxIds(self, entryId, authAsymId):
        tL = []
        try:
            tL = self.__ssD[entryId][authAsymId]["TAXID"]
        except Exception:
            pass
        return tL

    def __rebuildCache(self, **kwargs):
        mU = MarshalUtil()
        #
        siftsSummaryDirPath = kwargs.get("siftsSummaryDirPath", None)
        savePath = kwargs.get("saveCachePath", None)
        saveKwargs = kwargs.get("saveCacheKwargs", {"fmt": "pickle"})
        useCache = kwargs.get("useCache", True)
        entrySaveLimit = kwargs.get("entrySaveLimit", None)
        #
        ssD = {}
        try:
            if useCache and savePath and os.access(savePath, os.R_OK):
                ssD = mU.doImport(savePath, **saveKwargs)
            else:
                ssD = self.__getSummaryMapping(siftsSummaryDirPath)
                if entrySaveLimit:
                    ssD = {k: ssD[k] for k in list(ssD.keys())[:entrySaveLimit]}
                ok = mU.doExport(savePath, ssD, **saveKwargs)
                logger.debug("Saving SIFTS summary serialized data file %s (%d) status %r", savePath, len(ssD), ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return ssD

    def __getSummaryMapping(self, siftsSummaryDirPath):
        """
        """
        uD = self.__getUniprotChainMapping(siftsSummaryDirPath, "pdb_chain_uniprot.csv.gz")
        uSeqD = self.__getUniprotChainMapping(siftsSummaryDirPath, "uniprot_segments_observed.csv.gz")
        logger.info("uD length %d uSeqD %d", len(uD), len(uSeqD))
        #
        # --------------------
        #
        tD = self.__getTaxonomnyChainMapping(siftsSummaryDirPath, "pdb_chain_taxonomy.csv.gz")
        logger.info("Taxonomy mapping length %d", len(tD))
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["TAXID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #
        # --------------------
        #
        tD = self.__getCathChainMapping(siftsSummaryDirPath, "pdb_chain_cath_uniprot.csv.gz")
        logger.info("CATH mappinglength %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["CATHID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []

        tD = self.__getScopChainMapping(siftsSummaryDirPath, "pdb_chain_scop_uniprot.csv.gz")
        logger.info("SCOP mapping length %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["SCOPID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #
        tD = self.__getPfamChainMapping(siftsSummaryDirPath, "pdb_chain_pfam.csv.gz")
        logger.info("PFAM mapping length %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["PFAMID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #
        tD = self.__getEnzymeChainMapping(siftsSummaryDirPath, "pdb_chain_enzyme.csv.gz")
        logger.info("EC mapping length %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["ECID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #
        tD = self.__getInterProChainMapping(siftsSummaryDirPath, "pdb_chain_interpro.csv.gz")
        logger.info("InterPro mapping length %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["IPROID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #
        #
        tD = self.__getGeneOntologyChainMapping(siftsSummaryDirPath, "pdb_chain_go.csv.gz")
        logger.info("GO mapping length %d", len(tD))
        #
        #
        for entryId, eD in uSeqD.items():
            for chainId, _ in eD.items():
                uSeqD[entryId][chainId]["GOID"] = tD[entryId][chainId] if entryId in tD and chainId in tD[entryId] else []
        #

        #
        return uSeqD

    def __getGeneOntologyChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level GO mapping data.

        PDB,CHAIN,SP_PRIMARY,WITH_STRING,EVIDENCE,GO_ID
        101m,A,IPRO,InterPro:IPR000971,IEA,GO:0020037
        101m,A,IPRO,InterPro:IPR002335,IEA,GO:0015671
        101m,A,IPRO,InterPro:IPR002335,IEA,GO:0019825
        101m,A,IPRO,InterPro:IPR002335,IEA,GO:0020037
        101m,A,IPRO,InterPro:IPR012292,IEA,GO:0019825

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("CSV keys: %r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            prov = rowD["SP_PRIMARY"]
            evidenceCode = rowD["EVIDENCE"]
            goId = rowD["GO_ID"]
            dD = {"GO_ID": goId, "EV": evidenceCode, "PROV": prov}
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(dD)
        logger.info("GO data for %d entries", len(tD))
        return tD

    def __getInterProChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level InterPro mapping data.

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("CSV keys: %r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            interProId = rowD["INTERPRO_ID"]
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(interProId)
        logger.info("InterPro data for %d entries", len(tD))
        return tD

    def __getPfamChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level PFAM mapping data.

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("CSV keys: %r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            pfamId = rowD["PFAM_ID"]
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(pfamId)
        logger.info("EC data for %d entries", len(tD))
        return tD

    def __getEnzymeChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level EC mapping data.

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("CSV keys: %r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            ecId = rowD["EC_NUMBER"]
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(ecId)
        logger.info("EC data for %d entries", len(tD))
        return tD

    def __getCathChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level CATH mapping data.

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("CSV keys: %r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            cathId = rowD["CATH_ID"]
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(cathId)
        logger.info("CATH data for %d entries", len(tD))
        return tD

    def __getScopChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level SCOP mapping data.

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("%r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            scopId = rowD["SCOP_ID"]
            #
            tD.setdefault(entryId, {}).setdefault(chainId, []).append(scopId)
        #
        logger.info("SCOP data for %d entries", len(tD))
        return tD

    def __getTaxonomnyChainMapping(self, siftsSummaryDirPath, csvFileName):
        """ Integrated SIFTS summary instance-level taxonomy mapping data.

        # Taxonomy
        [('PDB', '101m'), ('CHAIN', 'A'), ('TAX_ID', '9755'), ('SCIENTIFIC_NAME', 'PHYCD')]

        """
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS summary file %s %d", csvFileName, len(rowDL))
        logger.debug("%r", list(rowDL[0].items()))
        tD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            taxId = rowD["TAX_ID"]
            tD.setdefault(entryId, {}).setdefault(chainId, {}).update({taxId: True})
        #
        logger.info("Taxonomy for %d entries", len(tD))
        return tD

    def __getUniprotChainMapping(self, siftsSummaryDirPath, csvFileName):
        """  Integrated SIFTS summary instance-level uniprot mapping data.
        """
        #
        #
        fp = os.path.join(siftsSummaryDirPath, csvFileName)
        rowDL = self.__readSiftsSummaryFile(fp)
        logger.info("Length of SIFTS UniProt summary file %s %d", csvFileName, len(rowDL))
        logger.debug("%r", list(rowDL[0].items()))
        uD = {}
        for rowD in rowDL:
            entryId = rowD["PDB"]
            chainId = rowD["CHAIN"]
            unpId = rowD["SP_PRIMARY"]
            #
            entitySeqBeg = int(rowD["RES_BEG"]) if rowD["RES_BEG"].isdigit() else None
            entitySeqEnd = int(rowD["RES_END"]) if rowD["RES_END"].isdigit() else None
            authSeqBeg = int(rowD["PDB_BEG"]) if rowD["PDB_BEG"].isdigit() else None
            authSeqEnd = int(rowD["PDB_END"]) if rowD["PDB_END"].isdigit() else None
            unpSeqBeg = int(rowD["SP_BEG"]) if rowD["SP_BEG"].isdigit() else None
            unpSeqEnd = int(rowD["SP_END"]) if rowD["SP_END"].isdigit() else None
            #
            # data.setdefault("system", {})["name"] = platform.system()
            #
            dD = {"UP": unpId, "BG": entitySeqBeg, "ND": entitySeqEnd, "AUBG": authSeqBeg, "AUND": authSeqEnd, "UBG": unpSeqBeg, "UND": unpSeqEnd}
            uD.setdefault(entryId, {}).setdefault(chainId, {}).setdefault("AL", []).append(dD)
            #
        logger.info("UniProt mapping for %d entries", len(uD))
        # -----
        return uD

    def __readSiftsSummaryFile(self, filePath):
        """ Read input SIFTS summary file and return a list of dictionaries.
        """
        try:
            mU = MarshalUtil()
            cL = mU.doImport(filePath, fmt="csv")
            logger.debug("Container list %d", len(cL))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return cL
