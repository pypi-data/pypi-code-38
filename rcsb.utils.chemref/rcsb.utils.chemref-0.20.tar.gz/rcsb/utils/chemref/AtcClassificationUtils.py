##
#  File:           AtcClassificationUtils.py
#  Date:           3-Apr-2019 jdw
#
#  Updated:
#
##
"""
  Extract ATC term descriptions from NCBO ATC flat files.

"""

import collections
import logging
import os.path
import sys

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class AtcClassificationUtils:
    """ Extract Atce assignments, term descriptions and Atc classifications
        from Atc flat files.

    """

    def __init__(self, **kwargs):
        #
        atcDirPath = kwargs.get("AtcDirPath", ".")
        useCache = kwargs.get("useCache", True)
        self.__version = kwargs.get("AtcVersion", "2018")
        #
        self.__mU = MarshalUtil(workPath=atcDirPath)

        self.__nD, self.__pD, self.__pdbD = self.__reload(atcDirPath, useCache=useCache, version=self.__version)
        #

    def getAtcVersion(self):
        return self.__version

    def getAtcSunIds(self, pdbId, authAsymId):
        """
         Get the sunid of the domain assignment for the assignment -

         aD[(pdbId, authAsymId)] = [(sunId, domainId, (authAsymId, resBeg, resEnd))]

         aD[(pdbId, authAsymId)] = [(domSunId, domainId, sccs, (authAsymId, resBeg, resEnd))]
        """
        try:
            return list(set([tup[0] for tup in self.__pdbD[(pdbId, authAsymId)]]))
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getAtcDomainNames(self, pdbId, authAsymId):
        try:
            return list(set([tup[1] for tup in self.__pdbD[(pdbId, authAsymId)]]))
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getAtcSccsNames(self, pdbId, authAsymId):
        try:
            return list(set([tup[2] for tup in self.__pdbD[(pdbId, authAsymId)]]))
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getAtcResidueRanges(self, pdbId, authAsymId):
        try:
            return [(tup[0], tup[1], tup[2], tup[3][0], tup[3][1], tup[3][2]) for tup in self.__pdbD[(pdbId, authAsymId)]]
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getAtcName(self, sunId):
        try:
            return self.__nD[sunId]
        except Exception:
            logger.debug("Undefined Atc sunId %r", sunId)
        return None

    def getIdLineage(self, sunId):
        pList = []
        try:
            pList.append(sunId)
            pt = self.__pD[sunId]
            while (pt is not None) and (pt != 0):
                pList.append(pt)
                pt = self.__pD[pt]
        except Exception as e:
            logger.exception("Failing for %r with %s", sunId, str(e))
        #
        pList.reverse()
        return pList

    def getNameLineage(self, sunId):
        try:
            return [self.getAtcName(cId) for cId in self.getIdLineage(sunId)]
        except Exception as e:
            logger.exception("Failing for %r with %s", sunId, str(e))
        return None

    def getTreeNodeList(self):
        return self.__exportTreeNodeList(self.__nD, self.__pD)

    def __reload(self, atcDirPath, useCache=True, version=None):
        pyVersion = sys.version_info[0]
        atcDomainPath = os.path.join(atcDirPath, "atc-py%s.pic" % str(pyVersion))
        #
        if useCache and self.__mU.exists(atcDomainPath):
            sD = self.__mU.doImport(atcDomainPath, fmt="pickle")
            logger.debug("Atce name length %d parent length %d assignments %d", len(sD["names"]), len(sD["parents"]), len(sD["assignments"]))
            nD = sD["names"]
            pD = sD["parents"]

        else:
            fn = "atc.csv" % version
            fp = os.path.join(atcDirPath, fn)
            logger.info("Fetch ATC term descriptions from source %s", fp)
            desL = self.__mU.doImport(fp, fmt="csv", rowFormat="dict", uncomment=False)
            #
            nD = self.__extractDescription(desL)
            # JDW TODO in progress
            pdbD = {}
            # dmD = self.__extractAssignments(claL)
            # pD = self.__extractHierarchy(hieL, nD)
            # pdbD = self.__buildAssignments(dmD)
            atcD = {"names": nD, "parents": pD, "assignments": pdbD}
            ok = self.__mU.doExport(atcDomainPath, atcD, fmt="pickle")
            logger.debug("Cache save status %r", ok)
            #
        return nD, pD, pdbD

    def __extractDescription(self, desL):
        """
        Example public data set from BioPortal -
        Class ID,Preferred Label,Synonyms,Definitions,Obsolete,CUI,Semantic Types,Parents,ATC LEVEL,Is Drug Class,Semantic type UMLS property

        http://purl.bioontology.org/ontology/UATC/A03AX13,silicones,,,false,C0037114,http://purl.bioontology.org/ontology/STY/T109|http://purl.bioontology.org/ontology/STY/T122,http://purl.bioontology.org/ontology/UATC/A03AX,5,,http://purl.bioontology.org/ontology/STY/T109|http://purl.bioontology.org/ontology/STY/T122
        http://purl.bioontology.org/ontology/UATC/J01DB07,cefatrizine,,,false,C0007545,http://purl.bioontology.org/ontology/STY/T195|http://purl.bioontology.org/ontology/STY/T109,http://purl.bioontology.org/ontology/UATC/J01DB,5,,http://purl.bioontology.org/ontology/STY/T195|http://purl.bioontology.org/ontology/STY/T109
        """
        nD = {}

        for fields in desL:
            if fields[1] in ["cl", "cf", "sf", "fa", "dm"]:
                nD[int(fields[0])] = str(fields[4]).strip()
        logger.debug("Length of name dictionary %d", len(nD))
        nD[0] = "root" if 0 not in nD else nD[0]

        return nD

    def __extractHierarchy(self, hieL, nD):
        """
        """
        pD = {}
        logger.debug("Length of input hierarchy list %d", len(hieL))
        for fields in hieL:
            chId = int(fields[0])
            #
            if chId not in nD:
                continue
            pId = int(fields[1]) if fields[1].isdigit() else None
            pD[chId] = pId
        #
        logger.info("Length of domain parent dictionary %d", len(pD))
        return pD

    def __exportTreeNodeList(self, nD, pD):
        """ Create node list from the Atce (sunid) parent and name/description dictionaries.

        """
        #
        pL = [0]
        logger.info("nD %d pD %d", len(nD), len(pD))
        # create child dictionary
        cD = {}
        for ctId, ptId in pD.items():
            cD.setdefault(ptId, []).append(ctId)
        #
        logger.debug("cD %d", len(cD))
        #
        idL = []
        for rootId in sorted(pL):
            visited = set([rootId])
            queue = collections.deque(visited)
            while queue:
                tId = queue.popleft()
                idL.append(tId)
                if tId not in cD:
                    # logger.warning("No children for Atc tId %r" % tId)
                    continue
                for childId in cD[tId]:
                    if childId not in visited:
                        queue.append(childId)
                        visited.add(childId)
        #
        dL = []
        for tId in idL:
            displayName = nD[tId] if tId in nD else None
            ptId = pD[tId] if tId in pD else None
            lL = self.getIdLineage(tId)
            #
            dD = {"id": tId, "name": displayName, "lineage": lL, "parents": [ptId], "depth": len(lL)}
            dL.append(dD)

        return dL
