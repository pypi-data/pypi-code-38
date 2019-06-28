import os

TIME_FMT = '%Y-%m-%d %H:%M:%S'
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOGFILE = '_metagenomi.log'
DECIMAL_ROUNDING = 3

AWS_CONFIG = {
    'DYNAMODB_TABLE_NAME': os.getenv('DYNAMODB_TABLE_NAME', 'mg-metadata-db'),
    'REGION': os.getenv('REGION', 'us-west-2'),
    'HMM_TABLE_NAME': os.getenv('HMM_TABLE_NAME', 'mg-hmms'),
    'SPACER_HIT_TABLE_NAME': os.getenv('SPACER_HIT_TABLE_NAME', 'spacer-hits'),
}
