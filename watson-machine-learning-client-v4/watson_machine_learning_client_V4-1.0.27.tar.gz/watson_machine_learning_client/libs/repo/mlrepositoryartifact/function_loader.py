################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.libs.repo.mlrepositoryartifact.function_artifact_loader  import FunctionArtifactLoader


class FunctionLoader(FunctionArtifactLoader):
    """
        Returns  Generic function instance associated with this function artifact.

        :return: function
        :rtype:
        """

    def function_instance(self):
        """
         :return: returns function path
         """
        return self.load()

    def download_function(self,path):
        """
         :return: returns function path
         """
        return self.load(path)

