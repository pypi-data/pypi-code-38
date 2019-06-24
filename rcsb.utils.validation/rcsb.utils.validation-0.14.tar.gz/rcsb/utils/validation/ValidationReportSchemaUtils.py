##
# File:    ValidationReportSchemaUtils.py
# Author:  J. Westbrook
# Date:    3-Feb-2019
# Version: 0.001
#
# Update:
#
#
##
"""
Various utilities for extracting metadata from  wwPDB validation report schema
and converting these details to a mmCIF extension dictionary.

"""
# pylint: disable=too-many-lines
import gzip
import logging
import re
import time

from mmcif.api.DataCategory import DataCategory
from mmcif.api.PdbxContainers import CifName
from mmcif.api.PdbxContainers import DataContainer
from mmcif.api.PdbxContainers import DefinitionContainer

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ValidationReportSchemaUtils(object):
    """Various utilities for extracting metadata from  wwPDB validation report schema
       and converting these details to a mmCIF extension dictionary.
    """

    def __init__(self):
        #
        # Schema provenance -
        #
        self.__schemaPath = "http://wwpdb.org/validation/schema/wwpdb_validation_v002.xsd"
        self.__schemaVersion = "V002"
        #
        # Translated dictionary provenance -
        #
        self.__dictName = "vrpt_mmcif_ext.dic"
        self.__dictDescription = "wwPDB Validation Report extension dictionary"
        self.__dictVersion = "0.001"
        self.__updateDate = time.strftime("%Y-%m-%d", time.localtime())
        self.__updateComment = "Preliminary translated version"
        #
        # XSD to CIF data type mapping -
        self.__typeMap = {"xsd:integer": "int", "xsd:string": "text", "xsd:decimal": "float3", "xsd:float": "float3", "xsd:boolean": "text"}
        #
        # Categories with implicit/inherited molecular context
        self.__requireMolecularContext = [
            "bond-outlier",
            "angle-outlier",
            "chiral-outlier",
            "plane-outlier",
            "clash",
            "symm-clash",
            "mog-bond-outlier",
            "mog-angle-outlier",
            "mog-torsion-outlier",
            "mog-ring-outlier",
        ]
        #
        # Inferred attributes that must be added to categories requiring molecular context (above)
        self.__contextAttributes = ["altcode", "chain", "ent", "model", "resname", "resnum", "said", "seq"]
        #
        #  Category name mapping dictionary
        #
        self.__catMappingD = {
            "wwPDB-validation-information": "pdbx_vrpt_info_notused",
            "Entry": "pdbx_vrpt_summary",
            "Model": "pdbx_vrpt_model_list",
            "ModelledSubgroup": "pdbx_vrpt_instance_results",
            "cyrange_domain": "pdbx_vrpt_cyrange_domain",
            "ModelledEntityInstance": "pdbx_vrpt_entity_instance_results",
            "chemical_shift_list": "pdbx_vrpt_chemical_shift_list",
            "unmapped_chemical_shift": "pdbx_vrpt_unmapped_chemical_shift",
            "unparsed_chemical_shift": "pdbx_vrpt_unparsed_chemical_shift",
            "missing_nmrstar_tag": "pdbx_vrpt_missing_nmrstar_tags",
            "random_coil_index": "pdbx_vrpt_random_coil_index",
            "chemical_shift_outlier": "pdbx_vrpt_chemical_shift_outlier",
            "referencing_offset": "pdbx_vrpt_referencing_offset",
            "assignment_completeness_well_defined": "pdbx_vrpt_assign_compl_well_defined",
            "assignment_completeness_full_length": "pdbx_vrpt_assign_compl_full_length",
            "programs": "pdbx_vrpt_sotfware_notused",
            "program": "pdbx_vrpt_software",
            "bond-outlier": "pdbx_vrpt_bond_outliers",
            "angle-outlier": "pdbx_vrpt_angle_outliers",
            "chiral-outlier": "pdbx_vrpt_stereo_outliers",
            "plane-outlier": "pdbx_vrpt_plane_outliers",
            "clash": "pdbx_vrpt_clashes",
            "symm-clash": "pdbx_vrpt_symmetry_clashes",
            "mog-bond-outlier": "pdbx_vrpt_mogul_bond_outliers",
            "mog-angle-outlier": "pdbx_vrpt_mogul_angle_outliers",
            "mog-torsion-outlier": "pdbx_vrpt_mogul_torsion_outliers",
            "mog-ring-outlier": "pdbx_vrpt_mogul_ring_outliers",
        }

        #
        # Attribute name mapping dictionary
        #
        self.__atMappingD = {
            "ordinal": "ordinal",
            "pdbid": "entry_id",
            "ent": "entity_id",
            "chain": "auth_asym_id",
            "said": "label_asym_id",
            "resname": "label_comp_id",
            "resnum": "auth_seq_id",
            "seq": "label_seq_id",
            "icode": "PDB_ins_code",
            "altcode": "label_alt_id",
            "model": "PDB_model_num",
            "PDB-deposition-date": "PDB_deposition_date",
            "PDB-revision-number": "PDB_revision_number",
            "PDB-revision-date": "PDB_revision_date",
            "PDB-resolution": "PDB_resolution",
            "PDB-resolution-low": "PDB_resolution_low",
            "PDB-R": "PDB_R",
            "PDB-Rfree": "PDB_Rfree",
            "protein-DNA-RNA-entities": "protein_DNA_RNA_entities",
            "CA_ONLY": "CA_ONLY",
            "XMLcreationDate": "report_creation_date",
            "coordinatesInputFilename": "coordinates_input_filename",
            "reflectionsInputFilename": "reflections_input_filename",
            "chemicalshiftsInputFilename": "chemical_shifts_input_filename",
            "attemptedValidationSteps": "attempted_validation_steps",
            "no-ligands-for-mogul": "no_ligands_for_mogul",
            "RestypesNotcheckedForBondAngleGeometry": "restypes_notchecked_for_bond_angle_geometry",
            "angles_rmsz": "angles_RMSZ",
            "bonds_rmsz": "bonds_RMSZ",
            "num_bonds_rmsz": "num_bonds_RMSZ",
            "num_angles_rmsz": "num_angles_RMSZ",
            "num-H-reduce": "num_H_reduce",
            "clashscore": "clashscore",
            "clashscore-full-length": "clashscore_full_length",
            "RNAsuiteness": "RNA_suiteness",
            "percent-rama-outliers": "percent_ramachandran_outliers",
            "percent-rama-outliers-full-length": "percent_ramachandran_outliers_full_length",
            "percent-rota-outliers": "percent_rotamer_outliers",
            "percent-rota-outliers-full-length": "percent_rotamer_outliers_full_length",
            "CCP4version": "ccp4version",
            "resol-high-from-reflectionsfile": "resol_high_from_reflectionsfile",
            "resol-low-from-reflectionsfile": "resol_low_from_reflectionsfile",
            "xtriage_input_columns": "xtriage_input_columns",
            "acentric_outliers": "acentric_outliers",
            "centric_outliers": "centric_outliers",
            "IoverSigma": "I_over_sigma",
            "numMillerIndices": "num_miller_indices",
            "WilsonBestimate": "Wilson_B_estimate",
            "WilsonBaniso": "Wilson_B_aniso",
            "DataAnisotropy": "data_anisotropy",
            "TransNCS": "trans_NSC",
            "TwinL": "twin_L",
            "TwinL2": "twin_L2",
            "TwinFraction": "twin_fraction",
            "B_factor_type": "B_factor_type",
            "DataCompleteness": "data_completeness",
            "DCC_R": "DCC_R",
            "DCC_Rfree": "DCC_Rfree",
            "DCC_refinement_program": "DCC_refinement_program",
            "num-free-reflections": "num_free_reflections",
            "percent-free-reflections": "percent_free_reflections",
            "RefmacVersion": "refmac_version",
            "EDS_R": "EDS_R",
            "EDS_resolution": "EDS_resolution",
            "EDS_resolution_low": "EDS_resolution_low",
            "Fo_Fc_correlation": "Fo_Fc_correlation",
            "babinet_b": "Babinet_b",
            "babinet_k": "Babinet_k",
            "bulk_solvent_b": "bulk_solvent_b",
            "bulk_solvent_k": "bulk_solvent_k",
            "percent-RSRZ-outliers": "percent_RSRZ_outliers",
            "nmr_models_consistency_flag": "nmr_models_consistency_flag",
            "cyrange_error": "cyrange_error",
            "cyrange_version": "cyrange_version",
            "nmrclust_error": "nmrclust_error",
            "nmrclust_version": "nmrclust_version",
            "nmrclust_representative_model": "nmrclust_representative_model",
            "medoid_model": "medoid_model",
            "nmrclust_number_of_outliers": "nmrclust_number_of_outliers",
            "nmrclust_number_of_models": "nmrclust_number_of_models",
            "nmrclust_number_of_clusters": "nmrclust_number_of_clusters",
            "cyrange_number_of_domains": "cyrange_number_of_domains",
            "chemical_shift_completeness": "chemical_shift_completeness",
            "chemical_shift_completeness_full_length": "chemical_shift_completeness_full_length",
            "panav_version": "panav_version",
            "rci_version": "rci_version",
            "shiftchecker_version": "shiftchecker_version",
            "percentilebins": "percentilebins",
            "no-percentile-property": "no_percentile_property",
            "absolute-percentile-RNAsuiteness": "absolute_percentile_RNA_suiteness",
            "numPDBids-absolute-percentile-RNAsuiteness": "num_PDBids_absolute_percentile_RNA_suiteness",
            "relative-percentile-RNAsuiteness": "relative_percentile_RNA_suiteness",
            "numPDBids-relative-percentile-RNAsuiteness": "num_PDBids_relative_percentile_RNA_suiteness",
            "low-resol-relative-percentile-RNAsuiteness": "low_resol_relative_percentile_RNA_suiteness",
            "high-resol-relative-percentile-RNAsuiteness": "high_resol_relative_percentile_RNA_suiteness",
            "absolute-percentile-clashscore": "absolute_percentile_clashscore",
            "numPDBids-absolute-percentile-clashscore": "num_PDBids_absolute_percentile_clashscore",
            "relative-percentile-clashscore": "relative_percentile_clashscore",
            "numPDBids-relative-percentile-clashscore": "num_PDBids_relative_percentile_clashscore",
            "low-resol-relative-percentile-clashscore": "low_resol_relative_percentile_clashscore",
            "high-resol-relative-percentile-clashscore": "high_resol_relative_percentile_clashscore",
            "absolute-percentile-percent-rama-outliers": "absolute_percentile_percent_ramachandran_outliers",
            "numPDBids-absolute-percentile-percent-rama-outliers": "num_PDBids_absolute_percentile_percent_ramachandran_outliers",
            "relative-percentile-percent-rama-outliers": "relative_percentile_percent_ramachandran_outliers",
            "numPDBids-relative-percentile-percent-rama-outliers": "num_PDBids_relative_percentile_percent_ramachandran_outliers",
            "low-resol-relative-percentile-percent-rama-outliers": "low_resol_relative_percentile_percent_ramachandran_outliers",
            "high-resol-relative-percentile-percent-rama-outliers": "high_resol_relative_percentile_percent_ramachandran_outliers",
            "absolute-percentile-percent-rota-outliers": "absolute_percentile_percent_rotamer_outliers",
            "numPDBids-absolute-percentile-percent-rota-outliers": "num_PDBids_absolute_percentile_percent_rotamer_outliers",
            "relative-percentile-percent-rota-outliers": "relative_percentile_percent_rotamer_outliers",
            "numPDBids-relative-percentile-percent-rota-outliers": "num_PDBids_relative_percentile_percent_rotamer_outliers",
            "low-resol-relative-percentile-percent-rota-outliers": "low_resol_relative_percentile_percent_rotamer_outliers",
            "high-resol-relative-percentile-percent-rota-outliers": "high_resol_relative_percentile_percent_rotamer_outliers",
            "absolute-percentile-DCC_Rfree": "absolute_percentile_DCC_Rfree",
            "numPDBids-absolute-percentile-DCC_Rfree": "num_PDBids_absolute_percentile_DCC_Rfree",
            "relative-percentile-DCC_Rfree": "relative_percentile_DCC_Rfree",
            "numPDBids-relative-percentile-DCC_Rfree": "num_PDBids_relative_percentile_DCC_Rfree",
            "low-resol-relative-percentile-DCC_Rfree": "low_resol_relative_percentile_DCC_Rfree",
            "high-resol-relative-percentile-DCC_Rfree": "high_resol_relative_percentile_DCC_Rfree",
            "absolute-percentile-percent-RSRZ-outliers": "absolute_percentile_percent_RSRZ_outliers",
            "numPDBids-absolute-percentile-percent-RSRZ-outliers": "num_PDBids_absolute_percentile_percent_RSRZ_outliers",
            "relative-percentile-percent-RSRZ-outliers": "relative_percentile_percent_RSRZ_outliers",
            "numPDBids-relative-percentile-percent-RSRZ-outliers": "num_PDBids_relative_percentile_percent_RSRZ_outliers",
            "low-resol-relative-percentile-percent-RSRZ-outliers": "low_resol_relative_percentile_percent_RSRZ_outliers",
            "high-resol-relative-percentile-percent-RSRZ-outliers": "high_resol_relative_percentile_percent_RSRZ_outliers",
            "nmrclust_cluster_id": "nmrclust_cluster_id",
            "nmrclust_representative": "nmrclust_representative",
            "ligand_num_clashes": "ligand_num_clashes",
            "ligand_num_symm_clashes": "ligand_num_symm_clashes",
            "ligand_clashes_outlier": "ligand_clashes_outlier",
            "ligand_chirality_outlier": "ligand_chirality_outlier",
            "cis_peptide": "cis_peptide",
            "NatomsEDS": "natoms_eds",
            "cyrange_domain_id": "cyrange_domain_id",
            "validate": "validate",
            "rsr": "RSR",
            "rscc": "RSRCC",
            "rsrz": "RSRZ",
            "owab": "OWAB",
            "avgoccu": "average_occupancy",
            "lig_rsrz_nbr_id": "lig_RSRZ_nbr_id",
            "ligRSRnbrMean": "lig_RSR_nbr_mean",
            "ligRSRnbrStdev": "lig_RSR_nbr_stdev",
            "ligRSRnumnbrs": "lig_RSR_numnbrs",
            "ligRSRZ": "lig_RSRZ",
            "rama": "ramachandran_class",
            "rota": "rotamer_class",
            "phi": "phi",
            "psi": "psi",
            "mogul-ignore": "mogul_ignore",
            "flippable-sidechain": "flippable_sidechain",
            "RNAscore": "RNA_score",
            "RNAsuite": "RNA_suite",
            "RNApucker": "RNA_pucker",
            "mogul_angles_rmsz": "mogul_angles_RMSZ",
            "mogul_bonds_rmsz": "mogul_bonds_RMSZ",
            "mogul_rmsz_numangles": "mogul_RMSZ_num_angles",
            "mogul_rmsz_numbonds": "mogul_RMSZ_num_bonds",
            "ligand_geometry_outlier": "ligand_geometry_outlier",
            "ligand_density_outlier": "ligand_density_outlier",
            "domain": "domain",
            "number_of_gaps": "number_of_gaps",
            "number_of_residues": "number_of_residues",
            "percentage_of_core": "percentage_of_core",
            "rmsd": "rmsd",
            "medoid_rmsd": "medoid_rmsd",
            "residue_string": "residue_string",
            "absolute_RSRZ_percentile": "absolute_RSRZ_percentile",
            "relative_RSRZ_percentile": "relative_RSRZ_percentile",
            "absolute_rama_percentile": "absolute_ramachandran_percentile",
            "relative_rama_percentile": "relative_ramachandran_percentile",
            "absolute_sidechain_percentile": "absolute_sidechain_percentile",
            "relative_sidechain_percentile": "relative_sidechain_percentile",
            "file_id": "file_id",
            "file_name": "file_name",
            "block_name": "block_name",
            "list_id": "list_id",
            "type": "type",
            "number_of_errors_while_mapping": "number_of_errors_while_mapping",
            "number_of_warnings_while_mapping": "number_of_warnings_while_mapping",
            "number_of_mapped_shifts": "number_of_mapped_shifts",
            "number_of_parsed_shifts": "number_of_parsed_shifts",
            "total_number_of_shifts": "total_number_of_shifts",
            "number_of_unparsed_shifts": "number_of_unparsed_shifts",
            "rescode": "rescode",
            "atom": "label_atom_id",
            "value": "value",
            "error": "error",
            "ambiguity": "ambiguity",
            "diagnostic": "diagnostic",
            "id": "id",
            "nmrstar_tag_description": "nmrstar_tag_description",
            "nmrstar_tag": "nmrstar_tag",
            "zscore": "zscore",
            "prediction": "prediction",
            "method": "method",
            "uncertainty": "uncertainty",
            "precision": "precision",
            "number_of_measurements": "number_of_measurements",
            "number_of_assigned_shifts": "number_of_assigned_shifts",
            "number_of_unassigned_shifts": "number_of_unassigned_shifts",
            "number_of_shifts": "number_of_shifts",
            "element": "element",
            "name": "name",
            "properties": "properties",
            "version": "version",
            "atom0": "atom0",
            "atom1": "atom1",
            "mean": "mean",
            "stdev": "stdev",
            "obs": "obs",
            "z": "Z",
            "link": "link",
            "atom2": "atom2",
            "problem": "problem",
            "improper": "improper",
            "omega": "omega",
            "planeRMSD": "plane_rmsd",
            "cid": "cid",
            "clashmag": "clashmag",
            "dist": "dist",
            "symop": "symop",
            "scid": "scid",
            "atoms": "atoms",
            "obsval": "obsval",
            "numobs": "numobs",
            "Zscore": "Zscore",
            "mindiff": "mindiff",
        }
        #
        self.__parentD = {
            "auth_asym_id": ("atom_site", "auth_asym_id", "code"),
            "auth_seq_id": ("atom_site", "label_seq_id", "code"),
            "label_comp_id": ("atom_site", "label_comp_id", "ucode"),
            "label_alt_id": ("atom_site", "label_alt_id", "code"),
            "PDB_ins_code": ("atom_site", "PDB_ins_id", "code"),
            "entity_id": ("atom_site", "label_entity_id", "code"),
            "label_asym_id": ("atom_site", "label_asym_id", "code"),
            "label_seq_id": ("atom_site", "label_seq_id", "int"),
            "entry_id": ("entry", "id", "code"),
        }
        #

    def buildDictionary(self, cD):
        """

        Args:
            cD (dict): input consolidated schema dictionary

        Returns:
            containerList (obj list) container list containing definition content
        """
        dictionaryMap = self.__exportdictionaryMapping(cD)
        cL = self.__buildDefinitions(cD, dictionaryMap)
        return cL

    def getDictionaryMap(self, cD, stringKey=True):
        """

        Args:
            cD (dict): input consolidated schema dictionary

        Returns:
            containerList (obj list) container list containing definition content
        """
        dictionaryMap = self.__exportdictionaryMapping(cD)
        if stringKey:
            tD = dictionaryMap["attributes"]
            sD = {}
            for kTup in tD:
                sTup = "|".join(kTup)
                sD[sTup] = tD[kTup]
            dictionaryMap["attributes"] = sD
        #
        return dictionaryMap

    def getAttributeOrder(self):
        ordD = {}
        icount = 1
        for ky in self.__atMappingD:
            ordD[ky] = icount
            icount += 1
        return ordD

    def getAttributeMap(self):
        return self.__atMappingD

    def __filterDescription(self, txt, mapD):
        """ Perform word replacement on the input text description.

        Args:
            txt: description text
            mapD: word map

        Returns:
            filtered txt string
        """
        if not txt:
            return txt
        iWordL = txt.split(" ")
        oWordL = []
        for word in iWordL:
            if "=" in word:
                tL = word.split("=")
                tstW = tL[0].strip('"').strip("'")
                if tstW in mapD:
                    oWord = word.replace(tstW, mapD[tstW])
                    oWordL.append(oWord)
            else:
                tstW = word.strip('"').strip("'")
                if tstW in mapD:
                    oWord = word.replace(tstW, mapD[tstW])
                    oWordL.append(oWord)
                else:
                    oWordL.append(word)
        #
        return " ".join(oWordL)

    def __dictionaryPragma(self, dictName, dictDescription, version, updateDate, comment):
        """ Add CIF dictionary header details including name, version and history.

;        Returns:
            Data container (object)  data container with dictionary history and version details
        """
        #
        dataH = DataContainer("pdbx_vrpt_ext.dic")
        dc = DataCategory("datablock", attributeNameList=["id", "description"])
        dc.append([dictName, dictDescription])
        dataH.append(dc)
        dc = DataCategory("dictionary", attributeNameList=["title", "datablock_id", "version"])
        dc.append([dictName, dictName, version])
        dataH.append(dc)
        dc = DataCategory("dictionary_history", attributeNameList=["version", "update", "revision"])
        dc.append([version, updateDate, comment])
        dataH.append(dc)
        return dataH

    def __buildDefinitions(self, cD, dictionaryMap):
        """ Construct an extension dictionary from input consolidate
            metadata extracted from the XML schema, and from the
            input schema name mapping dictionary.

        Args:
            cD (dict): consolidated xml schema data
            dictionaryMap (dict): mapping details for categories and attributes

        Returns:
#

        """
        cL = []
        cDat = self.__dictionaryPragma(self.__dictName, self.__dictDescription, self.__dictVersion, self.__updateDate, self.__updateComment)
        cL.append(cDat)
        #
        for catName, tD in cD.items():
            # atL = tD['attributes'] if 'attributes' in tD else []
            description = tD["description"] if "description" in tD else None
            description = self.__filterDescription(description, self.__catMappingD)
            mapCatName = dictionaryMap["categories"][catName] if catName in dictionaryMap["categories"] else catName
            if "notused" in mapCatName:
                continue
            if mapCatName in ["pdbx_vrpt_summary"]:
                cDef = self.__buildCategoryDefinition(mapCatName, description, ["entry_id"], [], ["RCSB_LOCAL"])
            else:
                cDef = self.__buildCategoryDefinition(mapCatName, description, ["ordinal"], [], ["RCSB_LOCAL"])
            cL.append(cDef)
            #
            atD = tD["attribD"] if "attribD" in tD else {}
            for atName in atD:
                mD = dictionaryMap["attributes"][(catName, atName)] if (catName, atName) in dictionaryMap["attributes"] else {}
                aDef = self.__buildAttributeDefinition(atD[atName], mD)
                cL.append(aDef)

        return cL

    def __buildAttributeDefinition(self, atD, mD):
        """ Construct an attribute definition from input attribute dictionary
            containing metadata extracted from the XML schema, and from the
            input schema name mapping dictionary.
        Args:
            atD (dict): attribute metadata dictionary
            dictionaryMap (dict): mapping details for categories and attributes

        Returns:
                Attribute definition (object)

        """
        #
        atName = atD["name"]
        catName = atD["category"]

        #
        mapAtName = mD["at"] if "at" in mD else atName
        mapCatName = mD["cat"] if "cat" in mD else catName
        pCat = mD["pCat"] if "pCat" in mD else None
        pAt = mD["pAt"] if "pAt" in mD else None
        pType = mD["pType"] if "pType" in mD else None
        #
        itemName = CifName.itemName(mapCatName, mapAtName)
        #
        aliasAtName = atD["aliasName"] if "aliasName" in atD else None
        aliasCatName = atD["aliasCategoryName"] if "aliasCategoryName" in atD else None
        #
        atDescription = atD["description"] if "description" in atD else None
        atDescription = self.__filterDescription(atDescription, self.__catMappingD)
        atDescription = self.__filterDescription(atDescription, self.__atMappingD)
        #
        mCode = "yes" if atD["mandatory"] == "mandatory" else "no"
        mCode = "yes" if mapAtName == "entry_id" else mCode
        #
        if atD["type"] not in self.__typeMap:
            logger.info("Unmapped type %r", atD["type"])
        #
        atType = self.__typeMap[atD["type"]] if atD["type"] in self.__typeMap else "UNKNOWN"
        #
        if atType == "text" and atDescription.find("comma separate") >= 0:
            atType = "alphanum-csv"
        if atType == "text" and "_date" in mapAtName and mapAtName != "report_creation_date":
            atType = "yyyy-mm-dd"
        #
        atType = pType if pType else atType

        if atType == "UNKNOWN":
            logger.info("Missing type mapping for %s %s %s", catName, atName, atD["type"])
        #
        defA = DefinitionContainer(itemName)
        #
        dc = DataCategory("item_description", attributeNameList=["description"])
        dc.append([atDescription])
        defA.append(dc)

        dc = DataCategory("item", attributeNameList=["name", "category_id", "mandatory_code"])
        dc.append([itemName, mapCatName, mCode])
        defA.append(dc)
        #
        dc = DataCategory("item_type", attributeNameList=["code"])
        dc.append([atType])
        defA.append(dc)

        dc = DataCategory("item_aliases", attributeNameList=["alias_name", "dictionary", "version"])
        dc.append([aliasCatName + "." + aliasAtName, self.__schemaPath, self.__schemaVersion])
        defA.append(dc)
        #
        # Note - expect boundaries in pairs and 'inclusive' of endpoints
        #
        if "minIncl" in atD and "maxIncl" in atD and atD["minIncl"] and atD["maxIncl"]:
            minB = atD["minIncl"]
            maxB = atD["maxIncl"]
            dc = DataCategory("item_range", attributeNameList=["minimum", "maximum"])
            dc.append([minB, minB])
            dc.append([minB, maxB])
            dc.append([maxB, maxB])
            defA.append(dc)
        else:
            if atType == "float" and ((mapAtName.find("percent_") >= 0) or (mapAtName.find("percentile_") >= 0)):
                dc = DataCategory("item_range", attributeNameList=["minimum", "maximum"])
                minB = "0.0"
                maxB = "100.0"
                dc.append([minB, minB])
                dc.append([minB, maxB])
                dc.append([maxB, maxB])
                defA.append(dc)
        #
        if "enum" in atD and isinstance(atD["enum"], list) and atD["enum"]:
            dc = DataCategory("item_enumeration", attributeNameList=["value", "detail"])
            for enumVal in atD["enum"]:
                dc.append([enumVal, "."])
            defA.append(dc)

        # -  add parent link relationships -
        if pCat and pAt:
            dc = DataCategory("item_linked", attributeNameList=["child_name", "parent_name"])
            parentItemName = CifName.itemName(pCat, pAt)
            dc.append([itemName, parentItemName])
            defA.append(dc)
        #
        #
        return defA

    def __buildCategoryDefinition(self, name, description, keyAttributeNames, examples, contexts):
        """Construct an attribute definition from input attribute dictionary
            containing metadata extracted from the XML schema, and from the
            input schema name mapping dictionary.

        Args:
            name (str): category name
            description (str): category description
            keyAttributeNames (list): key attribute names
            examples (list): category examples
            contexts (list): category contexts

        Returns:
            Definition container (object):

        """
        defC = DefinitionContainer(name)
        #
        dc = DataCategory("category", attributeNameList=["id", "description", "mandatory_code"])
        dc.append([name, description, "no"])
        defC.append(dc)
        #
        dc = DataCategory("category_key", attributeNameList=["name"])
        for keyAttributeName in keyAttributeNames:
            keyItemName = CifName.itemName(name, keyAttributeName)
            dc.append([keyItemName])
        defC.append(dc)

        dc = DataCategory("category_group", attributeNameList=["id"])
        dc.append(["inclusive_group"])
        dc.append(["validation_report_group"])
        defC.append(dc)
        # pdbx_category_context
        dc = DataCategory("pdbx_category_context", attributeNameList=["category_id", "type"])
        for cType in contexts:
            dc.append([name, cType])
        defC.append(dc)
        #
        dc = DataCategory("category_examples", attributeNameList=["detail", "case"])
        for example in examples:
            dc.append([".", example])
        defC.append(dc)

        return defC

    def __renameAttribute(self, atName):

        if atName in self.__atMappingD:
            return self.__atMappingD[atName]
        #
        if atName.find("-") > 0:
            return atName.replace("-", "_")
        elif atName.find("_") > 0:
            return atName
        else:
            # a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
            # t = a.sub(r'_\1', atName).lower()
            # return t
            return self.__camelToSnake(atName)
        #
        return atName

    def __exportdictionaryMapping(self, cD):
        """ Export a schema mapping file from input consolidated schema metadata.

        Args:
            cD: consolidated schema data

        Returns:
            typeMap {'categories': {}, 'attributes': {}}
        """
        atNameD = {}
        typeMap = {"categories": {}, "attributes": {}}
        for catName, tD in cD.items():
            mapCatName = self.__catMappingD[catName] if catName in self.__catMappingD else catName
            # logger.info("Mapping catName: %s to %s" % (catName, mapCatName))
            typeMap["categories"][catName] = mapCatName
            atD = tD["attribD"] if "attribD" in tD else {}
            #
            for atName, _ in atD.items():
                mapAtName = self.__renameAttribute(atName)
                atNameD[atName] = mapAtName
                # logger.info("Mapping atName %r to %r" % (atName, mapAtName))
                pTup = self.__parentD[mapAtName] if mapAtName in self.__parentD else (None, None, None)
                dD = {"cat": mapCatName, "at": mapAtName, "pCat": pTup[0], "pAt": pTup[1], "pType": pTup[2]}
                ky = (catName, atName)
                typeMap["attributes"][ky] = dD
        #
        # logger.info("AttributeMap %s" % json.dumps(atNameD, indent=3))
        return typeMap

    def readSchema(self, filePath, verbose=False):
        """ Extract the data organization and type details from the  XSD schema file
            describing the wwPDB validation data file.
        """
        cD = {}
        ns = "{http://www.w3.org/2001/XMLSchema}"
        xrt = self.__parse(filePath)
        #
        schD = self.__getSchema(xrt, ns)
        atD, stD = self.__getAttributeAndTypeDefs(xrt, ns)
        if verbose:
            self.__dumpSchema(schD, atD, stD)
            self.__traverseSchema(xrt, ns)
        # - add synthetic ordinal  -
        atD["ordinal"] = {"name": "ordinal", "type": "xsd:integer", "description": "Uniquely identifies each instance of this category.", "mandatory": "mandatory"}
        #
        cD = self.__consolidateSchema(schD, atD, stD)
        return cD

    def __consolidateSchema(self, schD, atD, stD):
        """

        Args:
            schD (schema):  extracted element and attribute details
            atD (dict): attribute type details
            stD (dict): named simple type details

        Returns:
            consolidated schema (dict):
        """
        defD = {}
        for catName, cD in schD.items():
            if "attributes" not in cD:
                continue
            catDescription = cD["description"] if "description" in cD else None
            defD[catName] = {"description": catDescription, "attribD": {}}
            attribD = {}
            extraL = self.__contextAttributes if catName in self.__requireMolecularContext else []
            if catName != "Entry":
                extraL.append("ordinal")
            for atName in cD["attributes"] + extraL:

                if "attribute_metadata" in cD and atName in cD["attribute_metadata"]:
                    aD = cD["attribute_metadata"][atName]
                elif atName in atD:
                    aD = atD[atName]
                else:
                    logger.info("Missing attribute info for %s %s", catName, atName)
                    continue

                atDescription = aD["description"] if "description" in aD else None
                atEnum = aD["enum"] if "enum" in aD else None
                atType = aD["type"] if "type" in aD else None
                minBoundIncl = aD["min"] if "min" in aD else None
                maxBoundIncl = aD["max"] if "max" in aD else None
                mCode = aD["mandatory"] if "mandatory" in aD else None
                if not atType:
                    logger.info("No type for catName %s atName %s  %r ", catName, atName, aD.items())
                if atType in stD:
                    logger.debug("Simple type used by catname %s atName %s type %r", catName, atName, stD[atType].items())
                    tD = stD[atType]
                    atEnum = tD["enum"] if "enum" in tD else atEnum
                    atDescription = tD["description"] if "description" in tD else atDescription
                    atType = tD["type"] if "type" in tD else atType
                    minBoundIncl = tD["min"] if "min" in tD else minBoundIncl
                    maxBoundIncl = tD["max"] if "max" in tD else maxBoundIncl
                    mCode = aD["mandatory"] if "mandatory" in aD else mCode
                attribD[atName] = {
                    "name": atName,
                    "category": catName,
                    "description": atDescription,
                    "type": atType,
                    "enum": atEnum,
                    "mandatory": mCode,
                    "minIncl": minBoundIncl,
                    "maxIncl": maxBoundIncl,
                    "aliasName": atName,
                    "aliasCategoryName": catName,
                }
                #
            defD[catName]["attribD"] = attribD
            #
        return defD

    def __getRestictions(self, el, ns):
        minBound = None
        maxBound = None
        enumL = []
        for ch in el:
            atD = ch.attrib
            if ch.tag == "{ns}enumeration".format(ns=ns):
                enumL.append(atD["value"])
            elif ch.tag == "{ns}minInclusive".format(ns=ns):
                minBound = atD["value"]
            elif ch.tag == "{ns}maxInclusive".format(ns=ns):
                maxBound = atD["value"]
        #
        rD = {"enum": enumL, "min": minBound, "max": maxBound}
        return rD

    def __processAttributeEl(self, el, ns):
        rD = {}

        if el.tag != "{ns}attribute".format(ns=ns):
            return rD
        #
        atD = el.attrib
        useOpt = atD["use"] if "use" in atD else None
        if "name" in atD:
            name = atD["name"]
            typ = atD["type"] if "type" in atD else None
            # mCode = atD['use'] if 'use' in atD else 'optional'
            desc = el.findtext("{ns}annotation/{ns}documentation".format(ns=ns))

            sTyp = el.find("{ns}simpleType/{ns}restriction".format(ns=ns)).attrib["base"] if el.find("{ns}simpleType/{ns}restriction".format(ns=ns)) else None
            #
            sTyp = el.find("{ns}simpleType/{ns}union".format(ns=ns)).attrib["memberTypes"].split(" ")[0] if el.find("{ns}simpleType/{ns}union".format(ns=ns)) is not None else sTyp
            #
            oTyp = sTyp if sTyp else typ
            rD = {"name": name, "type": oTyp, "description": desc}
            #
            if sTyp:
                rEl = el.find("{ns}simpleType/{ns}restriction".format(ns=ns))
                resD = self.__getRestictions(rEl, ns)
                for k, v in resD.items():
                    if v:
                        rD[k] = v
        elif "ref" in atD:
            rD = {"ref": atD["ref"]}

        if useOpt:
            rD["mandatory"] = useOpt

        return rD

    def __processSimpleTypeEl(self, el, ns):
        rD = {}
        if el.tag != "{ns}simpleType".format(ns=ns):
            return rD
        #
        atD = el.attrib
        if "name" in atD:
            name = atD["name"]
            desc = el.findtext("{ns}annotation/{ns}documentation".format(ns=ns))
            sTyp = el.find("{ns}union".format(ns=ns)).attrib["memberTypes"].split(" ")[0] if el.find("{ns}union".format(ns=ns)) is not None else None
            #
            sTyp = el.find("{ns}restriction".format(ns=ns)).attrib["base"] if el.find("{ns}restriction".format(ns=ns)) else sTyp
            #
            #
            rD = {"name": name, "type": sTyp, "description": desc}
            if sTyp:
                rEl = el.find("{ns}restriction".format(ns=ns))
                if not rEl:
                    logger.debug("No restrictions for simpletype %s %s", name, sTyp)
                else:
                    resD = self.__getRestictions(rEl, ns)
                    for k, v in resD.items():
                        if v:
                            rD[k] = v
        else:
            # anonymous simpleType may include some restriction -
            rEl = el.find("{ns}restriction".format(ns=ns))
            if not rEl:
                logger.info("No restrictions for anonymous simpletype")
            else:
                resD = self.__getRestictions(rEl, ns)
                for k, v in resD.items():
                    if v:
                        rD[k] = v
        #
        logger.debug("Processed simpletype returns %r", rD.items())
        #
        return rD

    def __getAttributeAndTypeDefs(self, elTree, ns):
        # named attributes
        aD = {}
        # named simpleTypes
        stD = {}
        for el in elTree.getroot():
            atD = el.attrib
            #
            if el.tag == "{ns}attribute".format(ns=ns) and "name" in atD:
                aD[atD["name"]] = self.__processAttributeEl(el, ns)
            elif el.tag == "{ns}simpleType".format(ns=ns) and "name" in atD:
                stD[atD["name"]] = self.__processSimpleTypeEl(el, ns)
        return aD, stD

    def __processParentEl(self, el, ns):
        rD = {}

        if el.tag != "{ns}element".format(ns=ns):
            return rD
        #
        atD = el.attrib
        if "name" in atD:
            name = atD["name"]
            desc = el.findtext("{ns}annotation/{ns}documentation".format(ns=ns))
            cTyp = el.find("{ns}complexType".format(ns=ns))
            rD = {"name": name, "description": desc}
            cTyp = el.find("{ns}complexType".format(ns=ns))
            #
            if cTyp:
                atL = []
                inlineD = {}
                for ch in cTyp:
                    atD = ch.attrib
                    if ch.tag == "{ns}attribute".format(ns=ns):
                        tD = self.__processAttributeEl(ch, ns)
                        if "ref" in tD:
                            atL.append(tD["ref"])
                        elif "name" in tD:
                            atL.append(tD["name"])
                            inlineD[tD["name"]] = tD
                rD["attributes"] = atL
                rD["attribute_metadata"] = inlineD
        elif "ref" in atD:
            rD = {"ref": atD["ref"]}

        return rD

    def __getSchema(self, elTree, ns):
        """
        Traverse the schema tree from root and construct the schema hierarchy -
        Top-level named elements are mapped to category definitions

        """
        #
        pElD = {}
        for el in elTree.getroot():
            atD = el.attrib
            # Get named elements
            if el.tag == "{ns}element".format(ns=ns) and "name" in atD:
                pElD[atD["name"]] = self.__processParentEl(el, ns)

        return pElD

    def __parse(self, filePath):
        """ Parse the input XML data file and return ElementTree object.
        """
        tree = []
        if filePath[-3:] == ".gz":
            with gzip.open(filePath, mode="rb") as ifh:
                logger.debug("Parsing drugbank at %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed schema in %.2f seconds", time.time() - tV)
        else:
            with open(filePath, mode="rb") as ifh:
                logger.debug("Parsing drugbank at %s", filePath)
                tV = time.time()
                tree = ET.parse(ifh)
                logger.debug("Parsed schema in %.2f seconds", time.time() - tV)
        return tree

    def __dumpSchema(self, schD, atD, stD):
        """

        Args:
            schD: element dictionary
            atD:  attribute dictionary
            stD:  simple types dictionary

        Returns:
            True

        """
        for elName in schD:
            logger.info("Element name: %s", elName)
            logger.debug("          >>> %r", schD[elName]["attributes"])

        for ky in atD:
            logger.info(">> attribute dictionary aD %s %r", ky, atD[ky].keys())
        for ky in stD:
            logger.info(">> simple type dictionary stD %s %r", ky, stD[ky].keys())
        #
        return True

    def __traverseSchema(self, xrt, ns):
        """ Traverse the schema and covering/logging all elements and attributes.

        Args:
            xrt (object): Elementree root object
            ns (string):  namespace string

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

    # ---------- ------------- ------------- ------------- ------------- ------------- ------------- -------------
    def __camelToSnake(self, name):
        """ Convert camel case string to snake case.

        Args:
            name:

        Returns:
            name in snake case

        """
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
