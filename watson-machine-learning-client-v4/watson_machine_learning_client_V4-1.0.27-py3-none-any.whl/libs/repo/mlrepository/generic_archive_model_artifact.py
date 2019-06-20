from watson_machine_learning_client.libs.repo.mlrepository import ModelArtifact

class GenericArchiveModelArtifact(ModelArtifact):
    """
    Class representing archive model artifact
    """
    def __init__(self, uid, name, meta_props):
        """
        Constructor for Generic archive model artifact
        :param uid: unique id for Generic archive model artifact
        :param name: name of the model
        :param metaprops: properties of the model and model artifact
        """
        super(GenericArchiveModelArtifact, self).__init__(uid, name, meta_props)