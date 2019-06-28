##
# File: EntityPolymerExtractor.py
# Date: 19-Feb-2019  jdw
#
# Selected utilities to extract entity polymer mapping and feature data
# from the exchange database schema.
#
# Updates:
#
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import copy
import logging
import os

from rcsb.db.mongo.Connection import Connection
from rcsb.db.mongo.MongoDbUtil import MongoDbUtil
from rcsb.utils.io.MarshalUtil import MarshalUtil


logger = logging.getLogger(__name__)


class EntityPolymerExtractor(object):
    """ Utilities to extract polymer related data from entry and entity collections.

    """

    def __init__(self, cfgOb, **kwargs):
        self.__cfgOb = cfgOb
        self.__resourceName = "MONGO_DB"
        self.__mU = MarshalUtil()
        #
        self.__entryD, self.__authAsymIdIndex = self.__rebuildCache(**kwargs)
        #

    def __rebuildCache(self, **kwargs):
        savePath = kwargs.get("saveCachePath", None)
        saveKwargs = kwargs.get("saveCacheKwargs", {"fmt": "pickle"})
        useCache = kwargs.get("useCache", True)
        #
        cD = {"entryD": {}, "authIdxD": {}}
        try:
            if useCache and savePath and os.access(savePath, os.R_OK):
                cD = self.__mU.doImport(savePath, **saveKwargs)
            else:
                entryD = self.__selectEntries(**kwargs)
                entryD = self.__selectPolymerEntities(entryD, **kwargs)
                authIdxD = self.__buildIndices(entryD)
                cD["entryD"] = entryD
                cD["authIdxD"] = authIdxD
                if savePath:
                    ok = self.__mU.doExport(savePath, cD, **saveKwargs)
                    logger.info("Saved entity results (%d) status %r in %s", len(entryD), ok, savePath)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return cD["entryD"], cD["authIdxD"]

    def __buildIndices(self, entryD):
        indD = {}
        for entryId, eD in entryD.items():
            entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
            for entityId, pD in entityD.items():
                for authAsymId in pD["auth_asym_ids"]:
                    # avoid tuples for json serialization
                    # indD[(entryId, authAsymId)] = entityId
                    indD[entryId + "_" + authAsymId] = entityId
        return indD

    def getEntryCount(self):
        return len(self.__entryD)

    def getRefSeqAccessions(self, dbName):
        acL = []
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    for dD in pD["struct_ref"]:
                        if "pdbx_db_accession" in dD and dD["db_name"] == dbName:
                            acL.append(dD["pdbx_db_accession"])
            return list(set(acL))
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return acL

    def countRefSeqAccessions(self, dbName):
        cD = {}
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    iCount = 0
                    for dD in pD["struct_ref"]:
                        if "pdbx_db_accession" in dD and dD["db_name"] == dbName:
                            iCount += 1
                    cD[iCount] = cD[iCount] + 1 if iCount in cD else 1
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return cD

    def countRefSeqAccessionDbType(self):
        cD = {}
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    for dD in pD["struct_ref"]:
                        if "pdbx_db_accession" in dD and "db_name" in dD:
                            cD[dD["db_name"]] = cD[dD["db_name"]] + 1 if dD["db_name"] in cD else 1
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return cD

    def countRefSeqAccessionAny(self):
        cD = {}
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    iCount = len(pD["struct_ref"])
                    # if iCount == 0:
                    #    logger.info("entryId %r " % (entryId, entityId))
                    cD[iCount] = cD[iCount] + 1 if iCount in cD else 1
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return cD

    def getUniqueTaxons(self):
        #
        tD = {}
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    # logger.info("Entity dictionary %r", pD.keys())
                    if "rcsb_entity_source_organism" in pD:
                        for dd in pD["rcsb_entity_source_organism"]:
                            if "ncbi_taxonomy_id" in dd:
                                tD[dd["ncbi_taxonomy_id"]] = tD[dd["ncbi_taxonomy_id"]] + 1 if dd["ncbi_taxonomy_id"] in tD else 1
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        logger.info("Taxon coverage %d", len(tD))
        return tD

    def getOrigTaxons(self):
        #
        tD = {}
        try:
            for entryId, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for entityId, pD in entityD.items():
                    # logger.info("Entity dictionary %r", pD.keys())
                    if "original_taxonomy_ids" in pD:
                        for tV in pD["original_taxonomy_ids"]:
                            tD.setdefault(entryId, []).append((entityId, tV))
                if entryId not in tD:
                    logger.debug("No taxonomy for %s", entryId)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        logger.info("Taxon coverage %d", len(tD))
        return tD

    def countRefSeqAccessionByTaxon(self, dbNameList=None):
        #
        tD = {}
        iCount = 0
        #
        try:
            for _, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for _, pD in entityD.items():
                    # logger.info("Entity dictionary %r", pD.keys())
                    if "rcsb_entity_source_organism" in pD:
                        for dd in pD["rcsb_entity_source_organism"]:
                            if "ncbi_taxonomy_id" in dd:
                                tId = dd["ncbi_taxonomy_id"]
                                for dD in pD["struct_ref"]:
                                    if "pdbx_db_accession" in dD and "db_name" in dD:
                                        if dD["db_name"] in dbNameList:
                                            tD.setdefault(tId, []).append(dD["pdbx_db_accession"])
                                        iCount += 1
        except Exception as e:
            logger.exception("Failing with %s", str(e))

        logger.info("Total observed accessions %d", iCount)
        return tD

    def checkRefSeqAlignRange(self, dbName):
        ok = True
        try:
            eCount = 0
            aCount = 0
            tCount = 0
            for entryId, eD in self.__entryD.items():
                entityD = eD["selected_polymer_entities"] if "selected_polymer_entities" in eD else {}
                for entityId, pD in entityD.items():
                    for dD in pD["struct_ref"]:
                        if "db_name" in dD and dD["db_name"] == dbName:
                            if "pdbx_db_accession" in dD and "alignD" in dD and "pdbx_seq_one_letter_code" in dD and "pdbx_align_begin" in dD:
                                seqLen = len(dD["pdbx_seq_one_letter_code"])
                                dbBegin = 100000000
                                dbEnd = -1
                                refSeqDbBegin = dD["pdbx_align_begin"]
                                for authAsymId, alDL in dD["alignD"].items():
                                    tCount += 1
                                    difL = []
                                    for alD in alDL:
                                        tBeg = alD["db_align_beg"]
                                        tEnd = alD["db_align_end"]
                                        tDif = tEnd - tBeg + 1
                                        difL.append(tDif)
                                        dbBegin = min(tBeg, dbBegin)
                                        dbEnd = max(tEnd, dbEnd)

                                        # range is calculate on off -
                                        # if seqLen < dbEnd - dbBegin + 1:
                                        if seqLen < dbEnd - dbBegin and not refSeqDbBegin == dbBegin:
                                            fDif = sum(difL)
                                            logger.debug(
                                                "Bad alignment for %r %r %r %r (%d) seqLen %r (%d) dbBegin %r dbEnd %r difL %r tDif %r",
                                                entryId,
                                                entityId,
                                                authAsymId,
                                                alD["pdbx_strand_id"],
                                                len(alDL),
                                                seqLen,
                                                dbEnd - dbBegin + 1,
                                                dbBegin,
                                                dbEnd,
                                                difL,
                                                fDif,
                                            )
                                            aCount += 1

                            else:
                                eCount += 1
            logger.info("Incomplete %s struct_ref record count %d", dbName, eCount)
            logger.info("Inconsistent %s db reference alignments %d/%d", dbName, aCount, tCount)

        except Exception as e:
            logger.exception("Failing with %s", str(e))
            ok = False

        return ok

    def getEntityRefSeqAccessions(self, dbName, entryId, entityId):
        acL = []
        try:
            dL = self.__entryD[entryId]["selected_polymer_entities"][entityId]["struct_ref"]
            acL = list(set([d["pdbx_db_accession"] for d in dL if d["db_name"] == dbName]))
        except Exception as e:
            logger.exception("Failing with %s %r %r %s", dbName, entryId, entityId, str(e))
        return acL

    def __selectEntries(self, **kwargs):
        """  Return a dictionary of PDB entries satifying the input conditions (e.g. method, resolution limit)
        """

        dbName = kwargs.get("dbName", "pdbx_core")
        collectionName = kwargs.get("collectionName", "pdbx_core_entry")
        selectionQueryD = kwargs.get("entrySelectionQuery", {})
        #
        entryD = {}
        try:
            with Connection(cfgOb=self.__cfgOb, resourceName=self.__resourceName) as client:
                mg = MongoDbUtil(client)
                if mg.collectionExists(dbName, collectionName):
                    logger.info("%s %s document count is %d", dbName, collectionName, mg.count(dbName, collectionName))
                    qD = {}
                    if selectionQueryD:
                        qD.update(qD)
                    selectL = ["_entry_id", "rcsb_entry_container_identifiers"]
                    dL = mg.fetch(dbName, collectionName, selectL, queryD=qD)
                    logger.info("Selection %r fetch result count %d", selectL, len(dL))
                    #
                    for dD in dL:
                        if "_entry_id" not in dD:
                            continue
                        entryD[dD["_entry_id"]] = {}
                        #
                        if (
                            ("rcsb_entry_container_identifiers" in dD)
                            and ("polymer_entity_ids" in dD["rcsb_entry_container_identifiers"])
                            and dD["rcsb_entry_container_identifiers"]["polymer_entity_ids"]
                        ):
                            entryD[dD["_entry_id"]] = {"polymer_entity_ids": dD["rcsb_entry_container_identifiers"]["polymer_entity_ids"]}

        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return entryD
        #

    def __selectPolymerEntities(self, entryD, **kwargs):
        """  Skeleton entity selector recovering essential biological sequence mapping features
             for macromolecules (default type = protein).

              "1CP9": {
                  "polymer_entity_ids": [
                     "1",
                     "2"
                  ],
                  "selected_polymer_entities": {
                     "1": {
                        "rcsb_multiple_source_flag": "N",
                        "asym_ids": [
                           "A"
                        ],
                        "auth_asym_ids": [
                           "A"
                        ],
                        "entity_id": "1",
                        "type": "polypeptide(L)",
                        "rcsb_entity_polymer_type": "Protein",
                        "rcsb_entity_source_organism": [
                           {
                              "ncbi_taxonomy_id": 587,
                              "beg_seq_num": 1,
                              "end_seq_num": 205,
                              "ncbi_scientific_name": "Providencia rettgeri"
                           }
                        ],
                        "struct_ref": [
                           {
                              "id": "1",
                              "db_name": "UNP",
                              "pdbx_db_accession": "Q7WZI9",
                              "entity_id": "1",
                              "pdbx_seq_one_letter_code": "QSTQIKIERDNYGVPHIYANDTYSLFYGYGYA...",
                              "alignD": {
                                 "A": [
                                    {
                                       "align_id": "1",
                                       "ref_id": "1",
                                       "pdbx_PDB_id_code": "1CP9",
                                       "pdbx_strand_id": "A",
                                       "seq_align_beg": 1,
                                       "seq_align_end": 205,
                                       "pdbx_db_accession": "Q7WZI9",
                                       "db_align_beg": 24,
                                       "db_align_end": 228,
                                       "pdbx_auth_seq_align_beg": "1",
                                       "pdbx_auth_seq_align_end": "205",
                                       "rcsb_entity_id": "1"
                                    }
                                 ]
                              }
                           }
                        ]
                     },
                 "2": {
                        "rcsb_multiple_source_flag": "N",
                        "asym_ids": [
                           "B"
                        ],
                        "auth_asym_ids": [
                           "B"
                        ],
                        "entity_id": "2",
                        "type": "polypeptide(L)",
                        "rcsb_entity_polymer_type": "Protein",
                        "rcsb_entity_source_organism": [
                           {
                              "ncbi_taxonomy_id": 587,
                              "beg_seq_num": 1,
                              "end_seq_num": 553,
                              "ncbi_scientific_name": "Providencia rettgeri"
                           }
                        ],
                        "struct_ref": [
                           {
                              "id": "2",
                              "db_name": "UNP",
                              "pdbx_db_accession": "Q7WZI9",
                              "entity_id": "2",
                              "pdbx_seq_one_letter_code": "SNVWLVGKTKASGAKAILLNGPQFGWFNPAYTYGIGLHG",
                              "alignD": {
                                 "B": [
                                    {
                                       "align_id": "2",
                                       "ref_id": "2",
                                       "pdbx_PDB_id_code": "1CP9",
                                       "pdbx_strand_id": "B",
                                       "seq_align_beg": 1,
                                       "seq_align_end": 553,
                                       "pdbx_db_accession": "Q7WZI9",
                                       "db_align_beg": 285,
                                       "db_align_end": 837,
                                       "pdbx_auth_seq_align_beg": "1",
                                       "pdbx_auth_seq_align_end": "553",
                                       "rcsb_entity_id": "2"
                                    }
                                 ]
                              }
                           }
                        ]
                     }
                  }
                },

        """
        dbName = kwargs.get("dbName", "pdbx_core")
        collectionName = kwargs.get("collectionName", "pdbx_core_entity")
        resultKey = kwargs.get("resultKey", "selected_polymer_entities")

        entryLimit = kwargs.get("entryLimit", None)
        selectionQueryD = kwargs.get("entitySelectionQuery", {"entity_poly.rcsb_entity_polymer_type": "Protein"})
        #
        try:
            with Connection(cfgOb=self.__cfgOb, resourceName=self.__resourceName) as client:
                mg = MongoDbUtil(client)
                if mg.collectionExists(dbName, collectionName):
                    logger.info("%s %s document count is %d", dbName, collectionName, mg.count(dbName, collectionName))
                    selectL = [
                        "rcsb_entity_container_identifiers",
                        "entity.rcsb_multiple_source_flag",
                        "entity_poly.type",
                        "entity_poly.rcsb_entity_polymer_type",
                        "entity_poly.pdbx_seq_one_letter_code_can",
                        "rcsb_entity_source_organism.ncbi_taxonomy_id",
                        "rcsb_entity_source_organism.ncbi_scientific_name",
                        "rcsb_entity_source_organism.beg_seq_num",
                        "rcsb_entity_source_organism.end_seq_num",
                        "struct_ref.id",
                        "struct_ref.pdbx_db_accession",
                        "struct_ref.db_name",
                        "struct_ref.entity_id",
                        "struct_ref.pdbx_seq_one_letter_code",
                        "struct_ref.pdbx_align_begin",
                        "struct_ref_seq",
                        #
                        "entity_src_nat.pdbx_ncbi_taxonomy_id",
                        "entity_src_gen.pdbx_gene_src_ncbi_taxonomy_id",
                        "entity_src_gen.pdbx_host_org_ncbi_taxonomy_id",
                        "pdbx_entity_src_syn.ncbi_taxonomy_id",
                    ]
                    iCount = 0
                    for entryId in entryD:
                        #
                        if resultKey in entryD[entryId]:
                            continue
                        #
                        qD = {"_entry_id": entryId}
                        qD.update(selectionQueryD)
                        #
                        dL = mg.fetch(dbName, collectionName, selectL, queryD=qD)
                        logger.debug("%s query %r fetch result count %d", entryId, qD, len(dL))
                        eD = {}
                        for ii, dD in enumerate(dL, 1):
                            rD = {}
                            logger.debug("%s (%4d) d is %r", entryId, ii, dD)
                            if "entity" in dD:
                                rD["rcsb_multiple_source_flag"] = dD["entity"]["rcsb_multiple_source_flag"] if "rcsb_multiple_source_flag" in dD["entity"] else "N"
                            #
                            if "rcsb_entity_container_identifiers" in dD:
                                rD["asym_ids"] = dD["rcsb_entity_container_identifiers"]["asym_ids"] if "asym_ids" in dD["rcsb_entity_container_identifiers"] else []
                                rD["auth_asym_ids"] = dD["rcsb_entity_container_identifiers"]["auth_asym_ids"] if "auth_asym_ids" in dD["rcsb_entity_container_identifiers"] else []
                                rD["entity_id"] = dD["rcsb_entity_container_identifiers"]["entity_id"]
                            #
                            if "entity_poly" in dD:
                                rD["type"] = dD["entity_poly"]["type"] if "type" in dD["entity_poly"] else None
                                rD["rcsb_entity_polymer_type"] = dD["entity_poly"]["rcsb_entity_polymer_type"] if "rcsb_entity_polymer_type" in dD["entity_poly"] else None
                                rD["entity_polymer_length"] = (
                                    len(dD["entity_poly.pdbx_seq_one_letter_code_can"]) if "entity_poly.pdbx_seq_one_letter_code_can" in dD["entity_poly"] else 0
                                )
                            #
                            tL = []
                            if "rcsb_entity_source_organism" in dD:
                                for tD in dD["rcsb_entity_source_organism"]:
                                    tL.append(tD)
                            rD["rcsb_entity_source_organism"] = copy.copy(tL)
                            #
                            qDL = []
                            if "struct_ref" in dD:
                                for tD in dD["struct_ref"]:
                                    if "db_name" in tD:
                                        tD["db_name"] = str(tD["db_name"]).upper().strip()
                                        tD["db_name"] = "UNP" if tD["db_name"] in ["TREMBL"] else tD["db_name"]
                                    qDL.append(tD)
                                if "struct_ref_seq" in dD:
                                    for qD in qDL:
                                        refId = qD["id"]
                                        alignL = []
                                        for tD in dD["struct_ref_seq"]:
                                            if refId == tD["ref_id"]:
                                                alignL.append(tD)
                                        # qD['align_list'] = copy.copy(aL)
                                        for align in alignL:
                                            authAsymId = align["pdbx_strand_id"]
                                            qD.setdefault("alignD", {}).setdefault(authAsymId, []).append(align)

                            rD["struct_ref"] = qDL
                            #
                            taxIdL = []
                            if "entity_src_nat" in dD:
                                for tD in dD["entity_src_nat"]:
                                    if "pdbx_ncbi_taxonomy_id" in tD:
                                        taxIdL.append(tD["pdbx_ncbi_taxonomy_id"])
                            if "entity_src_gen" in dD:
                                for tD in dD["entity_src_gen"]:
                                    if "pdbx_gene_src_ncbi_taxonomy_id" in tD:
                                        taxIdL.append(tD["pdbx_gene_src_ncbi_taxonomy_id"])
                                    if "pdbx_host_org_ncbi_taxonomy_id" in tD:
                                        taxIdL.append(tD["pdbx_host_org_ncbi_taxonomy_id"])
                            if "pdbx_entity_src_syn" in dD:
                                for tD in dD["pdbx_entity_src_syn"]:
                                    if "ncbi_taxonomy_id" in tD:
                                        taxIdL.append(tD["ncbi_taxonomy_id"])
                            qL = []
                            for taxId in taxIdL:
                                ttL = [int(t.strip()) for t in taxId.split(",") if t.strip().isdigit()]
                                qL.extend(ttL)
                            logger.debug("TaxId list %r", qL)
                            rD["original_taxonomy_ids"] = copy.copy(list(set(qL)))
                            #
                            if "entity_id" in rD:
                                eD[rD["entity_id"]] = copy.copy(rD)

                        entryD[entryId][resultKey] = copy.copy(eD)

                        iCount += 1
                        if iCount % 1000 == 0:
                            logger.info("Completed fetch %d/%d entries", iCount, len(entryD))
                        if entryLimit and iCount >= entryLimit:
                            logger.info("Quitting after %d", iCount)
                            break

        except Exception as e:
            logger.exception("Failing with %s", str(e))

        return entryD
