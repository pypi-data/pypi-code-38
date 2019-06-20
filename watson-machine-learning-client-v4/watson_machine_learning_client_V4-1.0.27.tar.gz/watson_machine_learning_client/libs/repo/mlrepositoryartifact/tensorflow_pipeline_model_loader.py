################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from watson_machine_learning_client.libs.repo.mlrepositoryartifact.tensorflow_artifact_loader import TensorflowArtifactLoader
from watson_machine_learning_client.libs.repo.util.library_imports import LibraryChecker
from watson_machine_learning_client.libs.repo.base_constants import *

lib_checker = LibraryChecker()

if lib_checker.installed_libs[TENSORFLOW]:
    import tensorflow as tf

class TensorflowPipelineModelLoader(TensorflowArtifactLoader):
    """
        Returns Tensorflow Runtime  instance associated with this model artifact.

        :return: TensorflowArtifactRunTime instance
        :rtype: TensorflowRuntimeArtifact
        """
    def load_model(self,session=None,tags=None):
        return(self.model_instance(session,tags))



    def model_instance(self,session=None,tags=None):
        lib_checker.check_lib(TENSORFLOW)
        if session is None:
            session = tf.Session(graph=tf.Graph())
        elif session is not None:
            if not isinstance(session,tf.Session):
                raise TypeError("sess should be of type : %s" % tf.Session)

        if tags is None:
            tags = [tf.saved_model.tag_constants.SERVING]
        elif tags is not None:
            if not isinstance(tags,list):
                raise TypeError("tags should be of type : %s" % list)


        return self.load(session,tags)
