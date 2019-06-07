from enum import Enum, unique

@unique
class MLEngineType(Enum):
    WML = 'IBM Watson Machine Learning'
    SAGEMAKER = 'Amazon Sagemaker'
    CUSTOM = 'Custom Machine Learning Engine'
    SPSS = 'IBM SPSS C&DS'
    AZUREML = 'Microsoft Azure Machine Learning'

@unique
class ResetType(Enum):
    METRICS = 'metrics'
    MONITORS = 'monitors'
    DATAMART = 'datamart'
    MODEL = 'model'
    ALL = 'all'
