##
# File:    UniProtUtils.py
# Date:    14-Mar-2019
#
# JDW - Adapted from SBKB sources and bits from RCSB codes -
#
##

import logging

from rcsb.utils.io.UrlRequestUtil import UrlRequestUtil
from rcsb.utils.seq.UniProtReader import UniProtReader

try:
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

logger = logging.getLogger(__name__)


class UniProtUtils(object):
    """
    Manage fetch queries for UniProt entries and related annotations.

    XML entry data is parsed into a feature dictionary.

    """

    def __init__(self, **kwargs):
        self.__saveText = kwargs.get("saveText", False)
        self.__dataList = []
        #

    def fetchList(self, idList, maxChunkSize=200):
        """     Execute a fetch query for the input id list.
                The input list is filtered for variants (e.g. ids with appended '-#').

                Divide the input list into manageable chunks, fetch each chunk,
                and concatenate the result.

                Return dict: dictionary of parsed UniProt features

        """
        try:
            if self.__saveText:
                self.__dataList = []
            resultD = {}
            matchD = {}
            #
            searchIdList, variantD = self.__processIdList(idList)

            logger.debug("input id list %s", idList)
            logger.debug("search   list %s", searchIdList)
            logger.debug("variants      %s", variantD.items())

            if searchIdList is None or not searchIdList:
                return resultD, matchD
            #
            matchD = {inpId: {"searchId": searchIdList[ii]} for ii, inpId in enumerate(idList)}
            #
            searchIdList = list(set(searchIdList))
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
                    tD = self.__parseText(xmlText, variantD)
                    resultD.update(tD)
                    if self.__saveText:
                        self.__dataList.append(xmlText)
                else:
                    logger.info("Fetch %r status %r text %r", subList, ok, xmlText)

            #
            # Create a match dictionary for the input id list -
            #
            for _, sD in matchD.items():
                if "matched" in sD:
                    continue
                if sD["searchId"] in resultD:
                    sD.setdefault("matchedIds", []).append(sD["searchId"])
                    sD["matched"] = "primary"
                else:
                    for _, rD in resultD.items():
                        if sD["searchId"] in rD["accessions"]:
                            sD.setdefault("matchedIds", []).append(sD["searchId"])
                            sD["matched"] = "secondary"
                    if "matched" not in sD:
                        sD["matched"] = "none"

        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return resultD, matchD

    def writeUnpXml(self, filePath):
        with open(filePath, "w") as ofh:
            for data in self.__dataList:
                ofh.write(data)

    def __parseText(self, xmlText, variantD):
        """
        Parse the accumulated xml text for each chunk and store the parsed data in
        the internal result dictionary.

        variant id codes are regisistered with the parser so that the returned dictionary
        contains keys corresponding to the original input id list.

        """
        retD = {}
        ur = UniProtReader()
        try:
            logger.debug("variantD %r", variantD)
            for vId, aId in variantD.items():
                ur.addVariant(aId, vId)
            retD = ur.readString(xmlText)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return retD

    def __doRequest(self, idList, retryAltApi=True):
        ret, retCode = self.__doRequestPrimary(idList)
        if retryAltApi and retCode not in [200]:
            ret, retCode = self.__doRequestSecondary(idList)
        ok = retCode in [200]
        #
        return ok, ret

    def __doRequestPrimary(self, idList):
        """
        """
        baseUrl = "http://www.uniprot.org"
        endPoint = "uploadlists"
        hL = [("Accept", "application/xml")]
        pD = {"from": "ACC+ID", "to": "ACC", "format": "xml", "query": " ".join(idList)}
        ureq = UrlRequestUtil()
        return ureq.get(baseUrl, endPoint, pD, headers=hL)

    def __doRequestSecondary(self, idList):
        baseUrl = "https://www.ebi.ac.uk"
        endPoint = "proteins/api/proteins"
        #
        hL = [("Accept", "application/xml")]
        pD = {}
        pD["size"] = "-1"
        pD["accession"] = ",".join(idList)
        ureq = UrlRequestUtil()
        return ureq.get(baseUrl, endPoint, pD, headers=hL)

    def __processIdList(self, idList):
        """
        Filter the input id list for variants and create the list of unique
        searchable id codes.   Create a dictionary of variant identifiers and
        their corresponding searchable id codes.

        """
        variantD = {}
        tList = []
        #
        for tId in idList:
            # check for variant id
            idx = tId.find("-")
            if idx == -1:
                sId = tId
            else:
                sId = tId[0:idx]
                variantD[tId] = sId
            #
            tList.append(sId)
        #
        #
        return tList, variantD

    def __makeSubLists(self, num, iterable):
        args = [iter(iterable)] * num
        return ([e for e in t if e is not None] for t in zip_longest(*args))

    def __makeSubListsWithPadding(self, num, iterable, padvalue=None):
        "__sublist(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
        return zip_longest(*[iter(iterable)] * num, fillvalue=padvalue)
