################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.libs.repo.mlrepositoryartifact.generic_file_artifact_loader  import GenericFileArtifactLoader


class GenericFilePipelineModelLoader(GenericFileArtifactLoader):
    """
        Returns  Generic pipeline model instance associated with this model artifact.

        :return: pipeline model
        :rtype: spss.learn.Pipeline
        """
    def load_model(self):
        return(self.model_instance())


    def model_instance(self):
        """
         :return: returns Spss model path
         """
        return self.load()


    def pipeline_instance(self):
        """
         :return: returns Spss model path
         """
        return self.load()