##
# File:    ChemCompModelUtils.py
# Author:  J. Westbrook
# Date:    1-Nov-2018
#
# Updates:

##
"""
Utilities to read resource file containing compilation of CCDC models correspondences
for PDB chemical components.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging

from rcsb.utils.io.MarshalUtil import MarshalUtil

logger = logging.getLogger(__name__)


class ChemCompModelUtils(object):
    """
    """

    def __init__(self):
        self.__ns = None

    def __readCifFile(self, filePath):
        """ Read input CIF file and return a container list.
        """
        cL = []
        try:
            mU = MarshalUtil()
            cL = mU.doImport(filePath, fmt="mmcif")
            logger.debug("Container list %d", len(cL))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
        return cL

    def getMapping(self, modelFilePath):
        """

        Example:

        data_M_010_00001
            #
            _pdbx_chem_comp_model.id        M_010_00001
            _pdbx_chem_comp_model.comp_id   010
            #
            _pdbx_chem_comp_model_reference.model_id   M_010_00001
            _pdbx_chem_comp_model_reference.db_name    CSD
            _pdbx_chem_comp_model_reference.db_code    YARXEW
            #
            loop_
            _pdbx_chem_comp_model_feature.model_id
            _pdbx_chem_comp_model_feature.feature_name
            _pdbx_chem_comp_model_feature.feature_value
            M_010_00001 experiment_temperature 123.0
            M_010_00001 publication_doi        10.1021/cg200971f
            M_010_00001 r_factor               3.91
            M_010_00001 all_atoms_have_sites   Y
        #
        """
        rD = {}
        dataContainerL = self.__readCifFile(modelFilePath)

        for dataContainer in dataContainerL:
            logger.debug("Processing model %r", dataContainer.getName())
            cObj = dataContainer.getObj("pdbx_chem_comp_model")
            ccId = cObj.getValue("comp_id", 0)
            #
            if ccId not in rD:
                rD[ccId] = []

            tObj = dataContainer.getObj("pdbx_chem_comp_model_reference")
            for iRow in range(tObj.getRowCount()):
                dbName = tObj.getValue("db_name", iRow)
                dbCode = tObj.getValue("db_code", iRow)
                rD[ccId].append({"db_name": dbName, "db_code": dbCode})

        return rD
