##
#  File:           ScopClassificationUtils.py
#  Date:           3-Apr-2019 jdw
#
#  Updated:
#  24-Apr-2019  jdw Exclude the root node from the exported tree node list
##
"""
  Extract SCOPe assignments, term descriptions and SCOP classifications
  from SCOP flat files.

"""

import collections
import logging
import os.path
import sys

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class ScopClassificationUtils:
    """ Extract SCOPe assignments, term descriptions and SCOP classifications
        from SCOP flat files.

    """

    def __init__(self, **kwargs):
        #
        self.__scopDirPath = kwargs.get("scopDirPath", ".")
        useCache = kwargs.get("useCache", True)
        urlTarget = kwargs.get("scopTargetUrl", "http://scop.berkeley.edu/downloads/update")
        self.__version = kwargs.get("scopVersion", "2.07-2019-03-07")
        #
        self.__mU = MarshalUtil(workPath=self.__scopDirPath)
        self.__nD, self.__pD, self.__pdbD = self.__reload(urlTarget, self.__scopDirPath, useCache=useCache, version=self.__version)
        #

    def getScopVersion(self):
        return self.__version

    def getScopSunIds(self, pdbId, authAsymId):
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

    def getScopDomainNames(self, pdbId, authAsymId):
        try:
            return list(set([tup[1] for tup in self.__pdbD[(pdbId, authAsymId)]]))
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getScopSccsNames(self, pdbId, authAsymId):
        try:
            return list(set([tup[2] for tup in self.__pdbD[(pdbId, authAsymId)]]))
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getScopResidueRanges(self, pdbId, authAsymId):
        try:
            return [(tup[0], tup[1], tup[2], tup[3][0], tup[3][1], tup[3][2]) for tup in self.__pdbD[(pdbId, authAsymId)]]
        except Exception as e:
            logger.debug("Failing for %r %r with %s", pdbId, authAsymId, str(e))

        return []

    def getScopName(self, sunId):
        try:
            return self.__nD[sunId]
        except Exception:
            logger.debug("Undefined SCOP sunId %r", sunId)
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
            return [self.getScopName(cId) for cId in self.getIdLineage(sunId)]
        except Exception as e:
            logger.exception("Failing for %r with %s", sunId, str(e))
        return None

    def getTreeNodeList(self):
        return self.__exportTreeNodeList(self.__nD, self.__pD)

    #
    ###
    ###
    #
    def __reload(self, urlTarget, scopDirPath, useCache=True, version=None):
        pyVersion = sys.version_info[0]
        scopDomainPath = os.path.join(scopDirPath, "scop_domains-py%s.pic" % str(pyVersion))
        #
        # scopDomainPath = os.path.join(scopDirPath, "scop_domains.json")
        #
        if useCache and self.__mU.exists(scopDomainPath):
            sD = self.__mU.doImport(scopDomainPath, fmt="pickle")
            logger.debug("SCOPe name length %d parent length %d assignments %d", len(sD["names"]), len(sD["parents"]), len(sD["assignments"]))
            nD = sD["names"]
            pD = sD["parents"]
            pdbD = sD["assignments"]

        else:
            ok = False
            minLen = 1000
            logger.info("Fetch SCOPe name and domain assignment data using target URL %s", urlTarget)
            desL, claL, hieL = self.__fetchFromSource(urlTarget, version=version)
            #
            nD = self.__extractDescription(desL)
            dmD = self.__extractAssignments(claL)
            pD = self.__extractHierarchy(hieL, nD)
            pdbD = self.__buildAssignments(dmD)
            logger.info("nD %d dmD %d pD %d", len(nD), len(dmD), len(pD))
            scopD = {"names": nD, "parents": pD, "assignments": pdbD}
            if (len(nD) > minLen) and (len(pD) > minLen) and (len(pD) > minLen):
                ok = self.__mU.doExport(scopDomainPath, scopD, fmt="pickle")
            logger.debug("Cache save status %r", ok)
            #
        return nD, pD, pdbD

    def __fetchFromSource(self, urlTarget, version="2.07-2019-03-07"):
        """  Fetch the classification names and domain assignments from SCOPe repo.
        #
                dir.des.scope.2.07-2019-03-07.txt
                dir.cla.scope.2.07-2019-03-07.txt
                dir.hie.scope.2.07-2019-03-07.txt
        """
        fn = "dir.des.scope.%s.txt" % version
        url = os.path.join(urlTarget, fn)
        desL = self.__mU.doImport(url, fmt="tdd", rowFormat="list", uncomment=True)
        logger.info("Fetched URL is %s len %d", url, len(desL))
        #
        fn = "dir.cla.scope.%s.txt" % version
        url = os.path.join(urlTarget, fn)
        claL = self.__mU.doImport(url, fmt="tdd", rowFormat="list", uncomment=True)
        logger.info("Fetched URL is %s len %d", url, len(claL))
        #
        fn = "dir.hie.scope.%s.txt" % version
        url = os.path.join(urlTarget, fn)
        hieL = self.__mU.doImport(url, fmt="tdd", rowFormat="list", uncomment=True)
        logger.info("Fetched URL is %s len %d", url, len(hieL))
        #
        return desL, claL, hieL

    def __extractDescription(self, desL):
        """
        From  dir.des.scope.2.07-2019-03-07.txt:

        # dir.des.scope.txt
        # SCOPe release 2.07 (2018-03-02, last updated 2019-03-07)  [File format version 1.02]
        # http://scop.berkeley.edu/
        # Copyright (c) 1994-2019 the SCOP and SCOPe authors; see http://scop.berkeley.edu/about
        46456   cl      a       -       All alpha proteins
        46457   cf      a.1     -       Globin-like
        46458   sf      a.1.1   -       Globin-like
        46459   fa      a.1.1.1 -       Truncated hemoglobin
        46460   dm      a.1.1.1 -       Protozoan/bacterial hemoglobin

        116748  sp      a.1.1.1 -       Bacillus subtilis [TaxId: 1423]
        113449  px      a.1.1.1 d1ux8a_ 1ux8 A:
        46461   sp      a.1.1.1 -       Ciliate (Paramecium caudatum) [TaxId: 5885]
        14982   px      a.1.1.1 d1dlwa_ 1dlw A:
        100068  px      a.1.1.1 d1uvya_ 1uvy A:
        46462   sp      a.1.1.1 -       Green alga (Chlamydomonas eugametos) [TaxId: 3054]
        14983   px      a.1.1.1 d1dlya_ 1dly A:
        100067  px      a.1.1.1 d1uvxa_ 1uvx A:
        63437   sp      a.1.1.1 -       Mycobacterium tuberculosis, HbN [TaxId: 1773]
        164742  px      a.1.1.1 d2gkma_ 2gkm A:
        164743  px      a.1.1.1 d2gkmb_ 2gkm B:

        """
        nD = {}

        for fields in desL:
            if fields[1] in ["cl", "cf", "sf", "fa", "dm"]:
                nD[int(fields[0])] = str(fields[4]).strip()
        logger.debug("Length of name dictionary %d", len(nD))
        nD[0] = "root" if 0 not in nD else nD[0]

        return nD

    def __extractAssignments(self, claL):
        """
        returns:

            aD[sunId] = [(), ... ]
        From dir.cla.scope.2.07-2019-03-07.txt:

        # dir.cla.scope.txt
        # SCOPe release 2.07 (2018-03-02, last updated 2019-03-07)  [File format version 1.02]
        # http://scop.berkeley.edu/
        # Copyright (c) 1994-2019 the SCOP and SCOPe authors; see http://scop.berkeley.edu/about
        #
        old_sunId                  sccs  sunid
        d1ux8a_ 1ux8    A:      a.1.1.1 113449  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=116748,px=113449
        d1dlwa_ 1dlw    A:      a.1.1.1 14982   cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=46461,px=14982
        d1uvya_ 1uvy    A:      a.1.1.1 100068  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=46461,px=100068
        d1dlya_ 1dly    A:      a.1.1.1 14983   cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=46462,px=14983
        d1uvxa_ 1uvx    A:      a.1.1.1 100067  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=46462,px=100067
        d2gkma_ 2gkm    A:      a.1.1.1 164742  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=164742
        d2gkmb_ 2gkm    B:      a.1.1.1 164743  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=164743
        d2gl3a_ 2gl3    A:      a.1.1.1 164754  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=164754
        d2gl3b_ 2gl3    B:      a.1.1.1 164755  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=164755
        d1idra_ 1idr    A:      a.1.1.1 62301   cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=62301
        d1idrb_ 1idr    B:      a.1.1.1 62302   cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=62302
        d1rtea_ 1rte    A:      a.1.1.1 105096  cl=46456,cf=46457,sf=46458,fa=46459,dm=46460,sp=63437,px=105096

        """
        dmD = {}
        logger.info("Length of class list %d", len(claL))
        rng = rngL = tL = None
        for fields in claL:
            try:
                rngL = str(fields[2]).strip().split(",")
                # dmTupL = [(tt[0], tt[1]) for tt in for rng.split(":") in rngL]
                #
                dmTupL = []
                for rng in rngL:
                    tL = [t for t in str(rng).strip().split(":") if len(t)]
                    if len(tL) > 1:
                        rL = tL[1].split("-")
                        tt = (tL[0], rL[0], rL[1])
                    else:
                        tt = (tL[0], None, None)

                    dmTupL.append(tt)
                #
                # Get the sid of the domain  -
                #
                sfL = str(fields[5]).strip().split(",")
                dmfL = sfL[4].split("=")
                dmf = int(dmfL[1])

                #                                         old domid      sccs    sunid for domain assignment
                dmD[int(fields[4])] = (fields[1], dmTupL, fields[0], fields[3], dmf)
                #
            except Exception as e:
                logger.exception("Failing fields %r rngL %r rng %r tL %r with %s", fields, rngL, rng, tL, str(e))

        #
        #
        logger.info("Length of domain assignments %d", len(dmD))
        return dmD

    def __buildAssignments(self, dmD):
        """
            Input internal data structure with domain assignments -

            dmD[sunId] = (pdbId, [(authAsymId, begRes, endRes), ...], domain_name, sccs, sid_domain_assigned)

            Returns:

               aD[(pdbId, authAsymId)] = [(domSunId, domainId, sccs, (authAsymId, resBeg, resEnd))]


        """
        pdbD = {}
        for _, dTup in dmD.items():
            for rTup in dTup[1]:
                pdbD.setdefault((dTup[0], rTup[0]), []).append((dTup[4], dTup[2], dTup[3], rTup))
        return pdbD

    def __extractHierarchy(self, hieL, nD):
        """
        From dir.hie.scope.2.07-2019-03-07.txt:

        # dir.hie.scope.txt
        # SCOPe release 2.07 (2018-03-02, last updated 2019-03-07)  [File format version 1.01]
        # http://scop.berkeley.edu/
        # Copyright (c) 1994-2019 the SCOP and SCOPe authors; see http://scop.berkeley.edu/about
        0       -       46456,48724,51349,53931,56572,56835,56992,57942,58117,58231,58788,310555
        46456   0       46457,46556,46625,46688,46928,46954,46965,46996,47004,47013,47026,47039,47044,47049,47054,47059,47071,...,...
        46457   46456   46458,46548
        46458   46457   46459,46463,46532,74660,191420
        46459   46458   46460,190322

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
        """ Create node list from the SCOPe (sunid) parent and name/description dictionaries.

            Exclude the root node from the tree.

        """
        #
        rootId = 0
        pL = [rootId]
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
                    # logger.warning("No children for scop tId %r", tId)
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
            lL = self.getIdLineage(tId)[1:]
            #
            # d = {'id': str(tId), 'name': displayName, 'lineage': [str(t) for t in lL], 'parents': [str(ptId)], 'depth': len(lL)}
            if tId == rootId:
                continue
            elif ptId == rootId:
                dD = {"id": str(tId), "name": displayName, "depth": 0}
            else:
                dD = {"id": str(tId), "name": displayName, "parents": [str(ptId)], "depth": len(lL)}
            dL.append(dD)

        return dL
