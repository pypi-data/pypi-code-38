from json import dumps
from logging import info

from boto3 import client
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

from microcosm_sagemaker.metrics.models import MetricMode


class SageMakerMetrics:
    def __init__(self, graph):
        pass

    def create(self, model_name, metrics=[], hyperparameters={}, mode=MetricMode.TRAINING):
        # Metric dimensions allow us to analyze metric performance against the
        # hyperparameters of our model
        dimensions = [
            {
                "Name": key,
                "Value": value,
            }
            for key, value in hyperparameters.items()
        ]

        metric_data = [
            {
                "MetricName": f"{mode.value} {metric.name}",
                "Dimensions": dimensions,
                "Value": metric.value,
                "Unit": metric.unit.value,
                "StorageResolution": 1
            }
            for metric in metrics
        ]

        try:
            cloudwatch = client("cloudwatch")
            response = cloudwatch.put_metric_data(
                Namespace="/aws/sagemaker/" + model_name,
                MetricData=metric_data,
            )
        except (ClientError, NoCredentialsError, NoRegionError):
            info("CloudWatch publishing disabled")
            info(dumps(metric_data, indent=4))
            response = None

        return response
