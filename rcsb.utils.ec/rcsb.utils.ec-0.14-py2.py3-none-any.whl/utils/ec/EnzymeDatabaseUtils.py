##
# -*- coding: utf-8 -*-
#
# File:    EnzymeDatabaseUtils.py
# Author:  J. Westbrook
# Date:    24-Jan-2019
# Version: 0.001
#
# Update:
#
#
##
"""
Various utilities for extracting data Enzyme database export data files
and returning lineage details.
"""

import collections
import copy
import gzip
import logging
import os
import time

from bs4 import BeautifulSoup

from rcsb.utils.io.FileUtil import FileUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class EnzymeDatabaseUtils(object):
    """Various utilities for extracting data Enzyme database export data files
       and returning lineage details.
    """

    def __init__(self, **kwargs):
        #
        urlTarget = kwargs.get("urlTarget", "https://www.enzyme-database.org/downloads/enzyme-data.xml.gz")
        enzymeDirPath = kwargs.get("enzymeDirPath", ".")
        useCache = kwargs.get("useCache", True)
        clearCache = kwargs.get("clearCache", False)
        enzymeDataFileName = kwargs.get("enzymeDataFileName", "enzyme-data.json")

        self.__debug = False
        #
        self.__mU = MarshalUtil(workPath=enzymeDirPath)
        self.__enzD = self.__reload(urlTarget, enzymeDirPath, enzymeDataFileName=enzymeDataFileName, useCache=useCache, clearCache=clearCache)

    def getClass(self, ecId):
        try:
            return self.__enzD["class"][ecId]
        except Exception:
            pass
        return None

    def getLineage(self, ecId):
        try:
            return self.__enzD["lineage"][ecId]
        except Exception:
            pass
        return None

    def getTreeNodeList(self):
        treeL = self.__exportTreeNodeList(self.__enzD)
        return treeL

    def __reload(self, urlTarget, dirPath, enzymeDataFileName, useCache=True, clearCache=False):
        """ Reload input XML database dump file and return data transformed lineage data objects.
'
        Returns:
            dictionary[ec_id] = {'name_list': ... , 'id_list': ... 'depth_list': ... }
        """
        enzD = {}
        #
        fU = FileUtil()
        fn = fU.getFileName(urlTarget)
        xmlFilePath = os.path.join(dirPath, fn)
        enzymeDataPath = os.path.join(dirPath, enzymeDataFileName)
        #
        #
        if clearCache:
            try:
                os.remove(xmlFilePath)
                os.remove(enzymeDataPath)
            except Exception:
                pass
        #
        if useCache and fU.exists(enzymeDataPath):
            enzD = self.__mU.doImport(enzymeDataPath, fmt="json")
        else:
            if useCache and fU.exists(xmlFilePath):
                logger.info("Using an existing resource file %s", xmlFilePath)
                ok = True
            else:
                logger.info("Fetching url %s to resource file %s", urlTarget, xmlFilePath)
                ok = fU.get(urlTarget, xmlFilePath)
            if ok:
                xrt = self.__parse(xmlFilePath)
                if self.__debug:
                    self.__traverse(xrt, ns="")
                rD = self.__extract(xrt)
                enzD = self.__build(rD)
                ok = self.__mU.doExport(enzymeDataPath, enzD, fmt="json", indent=3)
        return enzD

    def __build(self, rD):
        """  Build the list of ancestory classifiers for each leaf classifier.

        Source enzyme database exported data has the following organization:

         "class": [
                    {
                    "id": "1",
                    "class": "1",
                    "subclass": "1",
                    "subsubclass": "0",
                    "heading": "Acting on the CH-OH group of donors",
                    "note": "This subclass contains dehydrogenases that act on primary alcohols,",
                    "last_change": "2006-05-18 10:47:54"
                    }, ...

        "entry": [
                    {
                    "ec_num": "1.1.1.1",
                    "accepted_name": "alcohol dehydrogenase",
                    "reaction": "(1) a primary alcohol + NAD+ = an aldehyde + NADH + H+;;(2) a secondary alcohol + NAD+ = a ketone + NADH + H+",
                    "other_names": "aldehyde reductase; ADH; alcohol dehydrogenase (NAD); aliphatic alcohol dehydrogenase; ethanol dehydrogenase; NAD-dependent alcohol dehydrogenase;",
                    "sys_name": "alcohol:NAD+ oxidoreductase",
                    "comments": "A zinc protein. Acts on primary or secondary alcohols or hemi-acetals with very broad specificity; however the enzyme oxidizes ..... ",
                    "links": "BRENDA, EXPASY, GTD, IUBMB, KEGG, PDB, UM-BBD",
                    "class": "1",
                    "subclass": "1",
                    "subsubclass": "1",
                    "serial": "1",
                    "status": null,
                    "diagram": null,
                    "cas_num": "9031-72-5",
                    "glossary": null,
                    "last_change": "2012-02-17 13:19:04",
                    "id": "1"
                    }, ...


        Returns:
            dictionary[ec_id] = {'name_list': ... , 'id_list': ... 'depth_list': ... }

        """
        linD = {}
        cD = {}
        classD = {}
        #
        if "class" in rD:
            for dD in rD["class"]:
                clTup = tuple([dD[at] for at in ["class", "subclass", "subsubclass"]])
                val = self.__stripMarkup(dD["heading"])
                cD[clTup] = val
                classD[".".join(clTup)] = val

            for ecId in classD:
                cL = ecId.split(".")
                #
                tt = cL
                sscParent = tuple(tt)
                tt = cL[:-1]
                tt.append("0")
                scParent = tuple(tt)
                tt = cL[:-2]
                tt.extend(["0", "0"])
                cParent = tuple(tt)
                #
                try:
                    idL = [".".join(cL[:-2]), ".".join(cL[:-1]), ".".join(cL)]
                    classVal = cD[cParent] if cParent in cD else ""
                    subClassVal = cD[scParent] if scParent in cD else ""
                    subsubClassVal = cD[sscParent] if sscParent in cD else ""
                    nmL = [classVal, subClassVal, subsubClassVal]
                    depthL = [1, 2, 3]
                    #
                    logger.debug("%s idL %r", ecId, idL)
                    logger.debug("%s nmL %r", ecId, nmL)
                    fL = [t for t in cL if t != "0"]
                    fLen = len(fL)
                    for jj in range(1, fLen + 1):
                        tId = ".".join(cL[:jj])
                        if tId not in linD:
                            linD[tId] = [(depthL[ii], idL[ii], nmL[ii]) for ii in range(jj)]
                            logger.debug("%s %r", tId, linD[tId])
                except Exception as e:
                    logger.exception("Failing with %s", str(e))

        for k in sorted(classD):
            logger.debug("%10s %s", k, classD[k])
        #
        if "entry" in rD:
            for dD in rD["entry"]:
                if "serial" not in dD:
                    logger.error("Missing serial field in %r", dD)
                    continue
                cL = list([dD[at] for at in ["class", "subclass", "subsubclass", "serial"]])
                #
                tt = cL[:-1]
                sscParent = tuple(tt)
                tt = cL[:-2]
                tt.append("0")
                scParent = tuple(tt)
                tt = cL[:-3]
                tt.extend(["0", "0"])
                cParent = tuple(tt)
                #
                try:
                    idL = [".".join(cL[:-3]), ".".join(cL[:-2]), ".".join(cL[:-1]), ".".join(cL)]
                    classVal = cD[cParent] if cParent in cD else ""
                    subClassVal = cD[scParent] if scParent in cD else ""
                    subsubClassVal = cD[sscParent] if sscParent in cD else ""
                    serialValue = dD["accepted_name"] if "accepted_name" in dD else ""
                    if serialValue is None or not serialValue:
                        serialValue = ""
                        logger.debug("Missing accepted name data for %s", ".".join(cL))
                    else:
                        serialValue = self.__stripMarkup(serialValue)
                        classD[".".join(cL)] = serialValue

                    nmL = [classVal, subClassVal, subsubClassVal, serialValue]
                    depthL = [1, 2, 3, 4]
                    # linD['.'.join(cL)] = {'name_list': nmL, 'id_list': idL, 'depth_list': depthL}
                    for jj in range(1, 5):
                        ecId = ".".join(cL[:jj])
                        if ecId not in linD:
                            linD[ecId] = [(depthL[ii], idL[ii], nmL[ii]) for ii in range(jj)]

                except Exception as e:
                    logger.error("cL %r cParent %r scParent %r sscParent %r val %r", cL, cParent, scParent, sscParent, val)
                    logger.error("d is %r", dD)
                    logger.error("Failing with %s", str(e))
        #
        # strip 0 placeholders
        #
        rD = {}
        for ky in classD:
            ff = [t for t in ky.split(".") if t != "0"]
            rD[".".join(ff)] = classD[ky]

        #
        enzD = {"class": rD, "lineage": linD}
        return enzD

    def __exportTreeNodeList(self, enzD):
        """
        """
        # create parent dictionary
        #
        pL = []
        pD = {}
        for ecId in enzD["class"]:
            ff = ecId.split(".")
            if len(ff) == 1:
                pEcId = None
                pL.append(ecId)
            else:
                pEcId = ".".join(ff[:-1])
            logger.debug("ecId %s parent %s", ecId, pEcId)
            pD[ecId] = pEcId
        #
        logger.info("enzD %d pD %d", len(enzD["class"]), len(pD))
        cD = {}
        for cEcId, pEcId in pD.items():
            cD.setdefault(pEcId, []).append(cEcId)
        #
        logger.info("cD %d", len(cD))
        #
        idL = []
        for rootId in sorted(pL):
            visited = set([rootId])
            queue = collections.deque(visited)
            while queue:
                ecId = queue.popleft()
                idL.append(ecId)
                if ecId not in cD:
                    logger.debug("No children for ecId %s", ecId)
                    continue
                for childId in cD[ecId]:
                    if childId not in visited:
                        queue.append(childId)
                        visited.add(childId)
        #
        dL = []
        for ecId in idL:
            displayName = enzD["class"][ecId]
            pEcId = pD[ecId]

            lL = [t[1] for t in enzD["lineage"][ecId]]

            #
            if pEcId is None:
                dD = {"id": ecId, "name": displayName, "depth": 0}
            else:
                dD = {"id": ecId, "name": displayName, "parents": [pEcId], "depth": len(lL) - 1}
            dL.append(dD)

        return dL

    def __extract(self, xrt):
        """ Extract data from the input document and return a dictionary
            of objects containing rows of dictionaries with attribute naming.

        Args:
            xrt: ElementTree root element

        Returns:
            Extracted data (dict): dictionary organized by category with
                                   XML native data names.
        """
        rD = {}
        for el in xrt.getroot():
            logger.debug("-- Element tag %r name %r", el.tag, el.attrib["name"])
            # rD.setdefault(el.tag, []).append(q)
            #
            for ch in el:
                logger.debug("-- --> child element tag %r attrib %r", ch.tag, ch.attrib["name"])
                #
                if ch.tag == "table_data" and ch.attrib["name"] in ["class", "entry"]:
                    dL = self.__getTableData(ch)
                    rD[ch.attrib["name"]] = dL

                # for gch in ch:
                #    logger.debug("-- -- --> grand child element tag %r attrib count %r" % (gch.tag, len(gch.attrib)))
                #    for ggch in gch:
                #        logger.debug("-- -- --> grand child element tag %r attrib %r" % (ggch.tag, ggch.attrib['name']))
                # add parent cardinal attributes
        return rD
        #

    def __getTableData(self, el):
        """ Parse table data sections:

           Example --

             'table_data' {'name': 'cite'}
                'row' {}
                'field' {'name': 'cite_key'}
                'field' {'name': 'ec_num'}
                'field' {'name': 'ref_num'}
                'field' {'name': 'acc_no'}
                'field' {'name': 'last_change'}
                'row' {}
                'field' {'name': 'cite_key'}
                'field' {'name': 'ec_num'}
                'field' {'name': 'ref_num'}
                'field' {'name': 'acc_no'}
                'field' {'name': 'last_change'}
        """
        dL = []
        if el.tag != "table_data":
            return dL
        for ch in el:
            if ch.tag == "row":
                dD = {}
                for gch in ch:
                    if gch.tag == "field":
                        nm = gch.attrib["name"]
                        val = gch.text
                        dD[nm] = val
                        logger.debug(" Field %s val %r", nm, val)
                #
                dL.append(copy.copy(dD))
        return dL

    def __stripMarkup(self, text):
        try:
            tS = text.replace("&#151;", "-").replace("&amp;#151;", "-").replace(u"â€”", "-")
            bs = BeautifulSoup(tS, features="lxml")
            return bs.get_text()
        except Exception as e:
            logger.exception("Failing for %r with %s", text, str(e))
        return ""

    def __parse(self, filePath):
        """ Parse the input XML data file and return ElementTree root element.
        """
        tree = []
        if filePath[-3:] == ".gz":
            with gzip.open(filePath, mode="rb") as ifh:
                logger.debug("Parsing %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed %s %.2f seconds", filePath, time.time() - tV)
        else:
            with open(filePath, mode="rb") as ifh:
                logger.debug("Parsing %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed %s in %.2f seconds", filePath, time.time() - tV)
        return tree

    # -
    def __traverse(self, xrt, ns):
        """ Internal routine to traverse the dom covering/logging all elements and attributes.

        Args:
            xrt (object): ElementTree root element
            ns (str): XML namespace

        """

        for el in xrt.getroot():
            pEl = el.tag.replace(ns, "")
            logger.info("-- %r %r", pEl, el.attrib)
            for ch in el:
                chEl = ch.tag.replace(ns, "")
                logger.info("-- -->  %r %r", chEl, ch.attrib)
                if ch.text is not None and ch.text:
                    logger.info("-- -->  %s", ch.text)
                for gch in ch:
                    gchEl = gch.tag.replace(ns, "")
                    logger.info("-- -- -->  %r %r", gchEl, gch.attrib)
                    if gch.text is not None and gch.text:
                        logger.info("-- -- -->  %s", gch.text)
                    for ggch in gch:
                        ggchEl = ggch.tag.replace(ns, "")
                        logger.info("-- -- -- -->  %r %r", ggchEl, ggch.attrib)
                        if ggch.text is not None and ggch.text:
                            logger.info("-- -- -- -->  %s", ggch.text)
                        for gggch in ggch:
                            gggchEl = gggch.tag.replace(ns, "")
                            logger.info("-- -- -- -- -->  %r %r", gggchEl, gggch.attrib)
                            if gggch.text is not None and gggch.text:
                                logger.info("-- -- -- -- -->  %s", gggch.text)
