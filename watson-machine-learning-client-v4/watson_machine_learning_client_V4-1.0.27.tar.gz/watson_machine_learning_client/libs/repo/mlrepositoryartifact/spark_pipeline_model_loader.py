################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from .spark_artifact_loader import SparkArtifactLoader


class SparkPipelineModelLoader(SparkArtifactLoader):
    """
        Returns pipeline model instance associated with this model artifact.

        :return: pipeline model
        :rtype: pyspark.ml.PipelineModel
        """
    def model_instance(self):
        return self.load()