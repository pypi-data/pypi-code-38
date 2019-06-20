################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.libs.repo.mlrepositoryartifact.hybrid_artifact_loader import HybridArtifactLoader


class HybridPipelineModelLoader(HybridArtifactLoader):
    """
        Returns pipeline model instance associated with this model artifact.

        :return: model
        :rtype: hybrid.model
        """
    def model_instance(self, artifact=None):
        """
           :param artifact: query param string referring to "pipeline_model" or "full"
           Currently accepts:
           :return: returns a hybrid model content tar.gz file or pipeline_model.json
         """
        return self.load(artifact)
