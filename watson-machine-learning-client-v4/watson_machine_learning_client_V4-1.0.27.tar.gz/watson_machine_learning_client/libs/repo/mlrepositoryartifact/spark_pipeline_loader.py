################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from .spark_artifact_loader import SparkArtifactLoader


class SparkPipelineLoader(SparkArtifactLoader):
    """
    Returns pipeline instance associated with this pipeline artifact.

    :return: pipeline
    :rtype: pyspark.ml.Pipeline
    """
    def pipeline_instance(self):
        return self.load()
