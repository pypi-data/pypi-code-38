##
# File: ChemCompDataPrep.py
# Author:  J. Westbrook
# Date:  29-Jan-2019
#
# Utilities for processing chemical component definitions.
#
# Update:
#  31-Jan-2019 jdw make copy of all category and attribute lists on remove cycles.
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import copy
import logging

from mmcif.api.DictionaryApi import DictionaryApi

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class ChemCompDataPrep(object):
    """
    Integrate external annotations with local chemical reference data.

    """

    def __init__(self, cfgOb, **kwargs):
        #
        self.__cfgOb = cfgOb
        self.__workPath = kwargs.get("workPath", None)
        self.__mU = MarshalUtil(workPath=self.__workPath)
        self.__dApi = None
        #

    def exportContexts(self, jsonFilePath, includeContexts=None):
        includeContexts = includeContexts if includeContexts else ["WWPDB_LOCAL", "RCSB_LOCAL", "WWPDB_DEPRECATED", "WWPDB_DIFFRN_DATA", "CHEM_COMP_INT"]
        catD, atD = self.getContextInfo(includeContexts=includeContexts)
        exD = {"categoryContexts": catD, "attributeContexts": atD}
        ok = self.__mU.doExport(jsonFilePath, exD, fmt="json", indent=3)
        return ok

    def importContexts(self, jsonFilePath):
        cD = self.__mU.doImport(jsonFilePath, fmt="json")
        return cD

    def filterByContext(self, inpPath, outPath, contextD=None):
        containerList = self.__mU.doImport(inpPath, fmt="mmcif")
        self.__filterContextInPlace(containerList, contextD)
        ok = self.__mU.doExport(outPath, containerList, fmt="mmcif")
        return ok

    def __filterContextInPlace(self, containerList, contextD=None):
        """ Strip categories and attributes in any input context.
        """
        for container in containerList:
            #  - filter categories first
            catNameL = copy.deepcopy(container.getObjNameList())
            for catName in catNameL:
                logger.debug("Test category %s", catName)
                for context, fL in contextD["categoryContexts"].items():
                    if catName in fL:
                        logger.info("Category filtering on %s in context %s", catName, context)
                        container.remove(catName)
                        break
            #  - filter attributes in remaining categories
            catNameL = copy.deepcopy(container.getObjNameList())
            for catName in catNameL:
                cObj = container.getObj(catName)
                atNameL = copy.deepcopy(cObj.getAttributeList())
                for atName in atNameL:
                    for context, fL in contextD["attributeContexts"].items():
                        if {"cat": catName, "at": atName} in fL:
                            logger.info("Attribute filter in category %s attribute %s", catName, atName)
                            cObj.removeAttribute(atName)

    def getContextInfo(self, includeContexts=None):
        """
        """
        includeContexts = includeContexts if includeContexts else ["WWPDB_LOCAL"]
        dictLocator = self.__cfgOb.getPath("PDBX_DICT_LOCATOR", sectionName=self.__cfgOb.getDefaultSectionName())
        containerList = self.__mU.doImport(dictLocator, fmt="mmcif-dict")
        self.__dApi = DictionaryApi(containerList=containerList, consolidate=True, replaceDefinition=True, verbose=True)
        categoryList = self.__dApi.getCategoryList()
        dictSchema = {catName: self.__dApi.getAttributeNameList(catName) for catName in categoryList}
        categoryContextIndex, attributeContextIndex = self.__indexContexts(dictSchema, includeContexts=includeContexts)
        return categoryContextIndex, attributeContextIndex
        #

    def __indexContexts(self, dictSchema, includeContexts=None):
        """  Extract the category an item level dictionary contexts.
        """
        includeContexts = includeContexts if includeContexts else ["WWPDB_LOCAL"]
        catIndex = {}
        atIndex = {}
        for catName in dictSchema:
            for cV in self.__dApi.getCategoryContextList(catName):
                if includeContexts and cV in includeContexts:
                    catIndex.setdefault(cV, []).append(catName)

            for atName in dictSchema[catName]:
                for cV in self.__dApi.getContextList(catName, atName):
                    if includeContexts and cV in includeContexts:
                        atIndex.setdefault(cV, []).append({"cat": catName, "at": atName})
        return catIndex, atIndex
