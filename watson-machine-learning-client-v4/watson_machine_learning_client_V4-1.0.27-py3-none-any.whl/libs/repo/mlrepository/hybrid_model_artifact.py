from watson_machine_learning_client.libs.repo.mlrepository import ModelArtifact


class HybridModelArtifact(ModelArtifact):
    """
    Class representing Hybrid model artifact
    """
    def __init__(self, uid, name, meta_props):
        """
        Constructor for Hybrid model artifact
        :param uid: unique id for Hybrid model artifact
        :param name: name of the model
        :param metaprops: properties of the model and model artifact
        """
        super(HybridModelArtifact, self).__init__(uid, name, meta_props)

