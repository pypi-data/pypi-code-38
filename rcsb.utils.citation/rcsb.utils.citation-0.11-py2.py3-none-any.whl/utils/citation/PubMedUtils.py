##
# File:    PubMedUtils.py
# Date:    27-Apr-2019
#
# JDW - Adapted from SBKB sources and bits from RCSB codes -
#
##

import copy
import logging
import sys
import time

from rcsb.utils.citation.PubMedReader import PubMedReader
from rcsb.utils.io.UrlRequestUtil import UrlRequestUtil

try:
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

logger = logging.getLogger(__name__)


class PubMedUtils(object):
    """
    Manage fetch queries for PubMed entries and related annotations.

    XML entry data is parsed into a feature dictionary.

    """

    def __init__(self, **kwargs):
        self.__saveText = kwargs.get("saveText", False)
        self.__dataList = []
        self.__waitSeconds = kwargs.get("waitSeconds", 1)
        #

    def fetchList(self, idList, maxChunkSize=200):
        """     Execute a fetch query for the input id list.

                Divide the input list into manageable chunks, fetch each chunk,
                and concatenate the result.

                Return dict: dictionary of parsed PubMed features

        """
        try:
            if self.__saveText:
                self.__dataList = []
            resultD = {}
            #
            searchIdList = list(set(idList))

            logger.debug("input id list %s", idList)
            logger.debug("search   list %s", searchIdList)

            if not searchIdList:
                return resultD
            #
            subLists = self.__makeSubLists(maxChunkSize, searchIdList)
            numLists = len(searchIdList) / maxChunkSize + 1

            for ii, subList in enumerate(subLists):
                logger.debug("Fetching subList %r", subList)
                logger.info("Starting fetching for sublist %d/%d", ii + 1, numLists)
                #
                ok, xmlText = self.__doRequest(subList)
                logger.debug("Status %r", ok)
                #
                # Filter possible simple text error messages from the failed queries.
                #
                if (xmlText is not None) and not xmlText.startswith("ERROR"):
                    tD = self.__parseText(xmlText)
                    if tD:
                        resultD.update(tD)
                    if self.__saveText:
                        self.__dataList.append(xmlText)
                else:
                    logger.info("Fetch %r status %r text %r", subList, ok, xmlText)
                time.sleep(self.__waitSeconds)

        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return resultD

    def writeUnpXml(self, filePath):
        with open(filePath, "w") as ofh:
            for data in self.__dataList:
                ofh.write(data)

    def getJournalIndex(self, filePath):
        """
        --------------------------------------------------------
        JrId: 1
        JournalTitle: AADE editors' journal
        MedAbbr: AADE Ed J
        ISSN (Print): 0160-6999
        ISSN (Online):
        IsoAbbr: AADE Ed J
        NlmId: 7708172
        --------------------------------------------------------

        """
        rL = []
        dD = {}
        with open(filePath, "r") as ifh:
            for line in ifh:
                if "----" in line and "journal_title" in dD:
                    logger.debug("line %r: %r", line, dD)
                    rL.append(copy.copy(dD))
                    dD = {}
                #
                fields = [f.strip() for f in line[:-1].split(":")]
                #
                if fields[0] == "JournalTitle":
                    dD["journal_title"] = fields[1:]
                if fields[0] == "IsoAbbr":
                    dD["iso_abbrev"] = fields[1:]
                if fields[0] in ["ISSN (Print)"]:
                    dD["issn_print"] = fields[1:]
                if fields[0] in ["ISSN (Online)"]:
                    dD["issn_online"] = fields[1:]
        #
        logger.info("JOurnal length %d", len(rL))
        return rL

    def __parseText(self, xmlText):
        """
        Parse the accumulated xml text for each chunk and store the parsed data in
        the internal result dictionary.

        """
        rD = {}
        ur = PubMedReader()
        try:
            rD = ur.readString(xmlText)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        #
        logger.debug("rD %r", rD)
        return rD

    def __doRequest(self, idList, retryAltApi=True):
        _ = retryAltApi
        ret, retCode = self.__doRequestPrimary(idList)
        ok = retCode in [200]
        #
        if sys.version_info[0] == 2:
            return ok, ret.encode("utf-8")
        else:
            return ok, ret

    def __doRequestPrimary(self, idList):
        """
              http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=ID1,ID2,...
        """
        baseUrl = "http://eutils.ncbi.nlm.nih.gov"
        endPoint = "entrez/eutils/efetch.fcgi"
        hL = [("Accept", "application/xml")]
        pD = {"db": "pubmed", "retmode": "xml", "id": ",".join(idList)}
        ureq = UrlRequestUtil()
        return ureq.get(baseUrl, endPoint, pD, headers=hL)

    def __makeSubLists(self, num, iterable):
        args = [iter(iterable)] * num
        return ([e for e in t if e is not None] for t in zip_longest(*args))

    def __makeSubListsWithPadding(self, num, iterable, padvalue=None):
        "__sublist(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
        return zip_longest(*[iter(iterable)] * num, fillvalue=padvalue)
