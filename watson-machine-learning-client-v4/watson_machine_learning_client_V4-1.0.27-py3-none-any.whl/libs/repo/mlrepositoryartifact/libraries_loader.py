################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.libs.repo.mlrepositoryartifact.libraries_artifact_loader import LibrariesArtifactLoader


class LibrariesLoader(LibrariesArtifactLoader):
    """
        Returns  Libraries instance associated with this library artifact.
        :return: library zip file
    """
    def download_library(self, file_path):
        return self.load(file_path)


