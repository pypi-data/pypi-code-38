
S3_PATH_URL = r's3:\/\/([a-z0-9A-Z-]+)\/([\x00-\x7F][^\n]+$)'

S3_ARN_PREFIX = 'arn:aws:s3:::'
S3_NAME = r'[a-z0-9-]+'
S3_ARN  = r'^(arn:aws:s3:::[a-z-]+)$'

OU_PATH = r'^([^\/][A-Za-z0-9\/]+[^\/]$)$|^(\/root)$|^([a-zA-Z0-9]+)$'

IAM_ROLE_NAME = r'^[a-zA-Z0-9-_]+$'
IAM_ROLE_ARN = r'^(arn:aws:iam::[0-9]{12}:role\/[a-zA-Z0-9-_]+$)'

LAMBDA_NAME = IAM_ROLE_NAME
LAMBDA_ARN = r'^(arn:aws:lambda:[a-z]{2}-[a-z]{1,12}-[0-9]{1}:[0-9]{12}:function\/[a-zA-Z0-9]+)$'

LAMBDA_LAYER_VERSION = r'(^[a-z]+:[0-9]+$)'
LAMBDA_LAYER_ARN = r'(^arn:aws:lambda:[a-z]{2}-[a-z]{1,12}-[0-9]{1}:[0-9]{12}:layer:[a-zA-Z0-9]+:[0-9]{1,10})'

KMS_KEY_ID = r'^([a-z0-9]{8}(-[a-z0-9-]{4}){3}-[a-z0-9]+)$'
KMS_KEY_ARN  = r'^(arn:aws:kms:[a-z]{2}-[a-z]{1,10}-[0-9]{1}:[0-9]{12}:key\/[a-z0-9]{8}(-[a-z0-9-]{4}){3}-[a-z0-9]+)$'
KMS_ALIAS = r'(^(alias/)([a-zA-Z0-9-_/]+)$)'
KMS_ALIAS_ARN  = r'^(arn:aws:kms:[a-z]{2}-[a-z]{1,10}-[0-9]{1}:[0-9]{12}:(^(alias/)([a-zA-Z0-9-_/]+)$))$'
