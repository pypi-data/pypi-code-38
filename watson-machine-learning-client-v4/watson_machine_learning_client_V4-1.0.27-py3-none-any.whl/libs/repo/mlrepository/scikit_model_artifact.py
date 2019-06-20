################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from watson_machine_learning_client.libs.repo.mlrepository import ModelArtifact


class ScikitModelArtifact(ModelArtifact):
    """
    Class representing model artifact.

    :param str uid: optional, uid which indicate that artifact already exists in repository service
    :param str name: optional, name of artifact
    :param MetaProps meta_props: optional, props used by other services
    """
    def __init__(self, uid, name, meta_props):
        super(ScikitModelArtifact, self).__init__(uid, name, meta_props)

    def pipeline_artifact(self):
        """
        Returns None. pipeline artifact for scikit model has not been implemented.

        :rtype: ModelArtifact
        """
        pass
