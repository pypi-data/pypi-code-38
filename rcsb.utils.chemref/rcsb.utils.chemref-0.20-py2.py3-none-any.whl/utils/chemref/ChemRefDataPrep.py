##
# File: ChemRefDataPrep.py
# Author:  J. Westbrook
# Date:  4-Dec-2018
#
# Very preliminary implementation for building loadable corresponding data from
# external resources (e.g. DrugBank).
#
# Update:
#  7-Jan-2019 jdw qualify default section name in config path lookup
# 16-Feb-2019 jdw add drugbank_container_identifiers ...
# 23-Mar-2019 jdw adjust item name affected_organisms
# 10-Apr-2019 jdw add atc_codes
##

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"


import logging

from rcsb.utils.chemref.DrugBankUtils import DrugBankUtils

# from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class ChemRefDataPrep(object):
    """
    Integrate external annotations with local chemical reference data.

    """

    def __init__(self, cfgOb, **kwargs):
        #
        self.__cfgOb = cfgOb
        self.__kwargs = kwargs
        self.__resourceName = "MONGO_DB"
        # self.__workPath = kwargs.get('workPath', None)
        # self.__sandboxPath = kwargs.get('sandboxPath', None)
        #
        # self.__mU = MarshalUtil(workPath=self.__workPath)
        #

    def getDocuments(self, extResource, exIdD):
        """
        """
        oL = []
        if extResource == "DrugBank":
            drugBankFilePath = self.__cfgOb.getPath("DRUGBANK_DATA_LOCATOR", sectionName=self.__cfgOb.getDefaultSectionName())
            dbDocL = self.fetchDocuments(extResource, drugBankFilePath)
            oL = []
            for dbDoc in dbDocL:
                if "drugbank_id" in dbDoc and dbDoc["drugbank_id"] in exIdD:
                    lD = self.buildDocument(extResource, dbDoc)
                    oL.append(lD)
                else:
                    logger.debug("dbDoc.keys() %r", list(dbDoc.keys()))
        return oL
        #

    def fetchDocuments(self, extResource, filePath):
        if extResource == "DrugBank":
            return self.__fetchDrugBankDocuments(filePath)
        else:
            return None

    def buildDocument(self, extResource, dbObj):
        if extResource == "DrugBank":
            return self.__buildDrugBankDocument(dbObj)
        else:
            return None

    def __fetchDrugBankDocuments(self, drugBankFilePath):
        """
        """
        dbu = DrugBankUtils()
        rL = dbu.read(drugBankFilePath)
        logger.info("DrugBank data object length %d", len(rL))
        # logger.info("DrugBank example keys %r", rL[0].keys())
        # logger.info("DrugBank example aliases %r", rL[0]['aliases'])
        return rL

    def __buildDrugBankDocument(self, dbObj):
        """
        Construct local loadable object from input DrugBank extracted data object
        conforming to the following category organization:

         _drugbank_info.drugbank_id
         _drugbank_info.name
         _drugbank_info.description
         _drugbank_info.synonyms
         _drugbank_info.brand_names
         _drugbank_info.affected_organisms
         _drugbank_info.indication
         _drugbank_info.pharmacology
         _drugbank_info.mechanism_of_action
         _drugbank_info.cas_number
         _drugbank_info.drug_categories
         _drugbank_info.drug_groups
         _drugbank_info.atc_codes


         _drugbank_target.ordinal
         _drugbank_target.name
         _drugbank_target.interaction_type
         _drugbank_target.target_actions
         _drugbank_target.organism_common_name
         _drugbank_target.reference_database_name
         _drugbank_target.reference_database_accession_code
         _drugbank_target.seq_one_letter_code

        """
        oD = {}
        oD["_drugbank_id"] = dbObj["drugbank_id"]
        oD["drugbank_container_identifiers"] = {"drugbank_id": dbObj["drugbank_id"]}

        dbiD = {}
        textKeys = [
            ("drugbank_id", "drugbank_id"),
            ("name", "name"),
            ("description", "description"),
            ("indication", "indication"),
            ("pharmacology", "pharmacology"),
            ("mechanism_of_action", "mechanism_of_action"),
            ("cas_number", "cas_number"),
        ]
        listKeys = [
            ("drug_categories", "drug_categories"),
            ("groups", "drug_groups"),
            ("aliases", "synonyms"),
            ("products", "brand_names"),
            ("affected_organisms", "affected_organisms"),
            ("atc_codes", "atc_codes"),
        ]
        # For category drugbank_info
        for textKey, docKey in textKeys:
            if textKey in dbObj and dbObj[textKey]:
                dbiD[docKey] = dbObj[textKey].replace("\r", "").replace("\n", " ")
        #
        for listKey, docKey in listKeys:
            if listKey in dbObj and dbObj[listKey]:
                dbiD[docKey] = list(dbObj[listKey])
            else:
                logger.debug("MISSING KEY %s", listKey)
        #
        oD["drugbank_info"] = dbiD
        #
        # For category drugbank_target -
        #
        tL = []
        if "target_interactions" in dbObj:
            for ii, tid in enumerate(dbObj["target_interactions"], 1):
                tD = {}
                tD["ordinal"] = ii
                tD["interaction_type"] = tid["category"]
                tD["name"] = tid["name"]
                if "organism" in tid:
                    tD["organism_common_name"] = tid["organism"]
                if "actions" in tid and tid["actions"]:
                    tD["target_actions"] = tid["actions"]
                if "amino-acid-sequence" in tid and tid["amino-acid-sequence"] and tid["amino-acid-sequence"]:
                    tD["seq_one_letter_code"] = "".join(tid["amino-acid-sequence"].split("\n")[1:])
                if "uniprot_ids" in tid and tid["uniprot_ids"]:
                    tD["reference_database_name"] = "UniProt"
                    tD["reference_database_accession_code"] = tid["uniprot_ids"]
                #
                tL.append(tD)
        #
        if tL:
            oD["drugbank_target"] = tL
        #
        return oD
