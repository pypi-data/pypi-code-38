from watson_machine_learning_client.libs.repo.mlrepository import ModelArtifact


class XGBoostModelArtifact(ModelArtifact):
    """
    Class representing xgboost model artifact
    """
    def __init__(self, uid, name, meta_props):
        """
        Constructor for xgboost model artifact
        :param uid: unique id for xgboost model artifact
        :param name: name of the model
        :param metaprops: properties of the model and model artifact
        """
        super(XGBoostModelArtifact, self).__init__(uid, name, meta_props)