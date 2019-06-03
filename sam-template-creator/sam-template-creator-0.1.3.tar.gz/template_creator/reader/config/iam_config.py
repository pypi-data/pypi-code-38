# sometimes the name used by the sdk does not match that required for IAM. These dictionaries map those exceptions.

PYTHON_EXCEPTIONS = {
    'alexaforbusiness': 'a4b',
    'apigateway': 'execute-api',
    'cloudhsmv2': 'cloudhsm',
    'dynamodbstreams': 'dynamodb',
    'efs': 'elasticfilesystem',
    'elb': 'elasticloadbalancing',
    'elbv2': 'elasticloadbalancing',
    'emr': 'elasticmapreduce',
    'lex-models': 'lex',
    'meteringmarketplace': 'aws-marketplace',
    'mobile': 'mobilehub',
    'mturk': 'mechanicalturk',
    'neptune': 'neptune-db',
    'pinpoint-sms-voice': 'sms-voice',
    'stepfunctions': 'states',
}

GO_EXCEPTIONS = {
    'acmpca': 'acm-pca',
    'alexaforbusiness': 'a4b',
    'apigateway': 'execute-api',
    'applicationautoscaling': 'application-autoscaling',
    'applicationdiscoveryservice': 'discovery',
    'cloudwatchevents': 'events',
    'cloudwatchlogs': 'logs',
    'cognitoidentity': 'cognito-identity',
    'cognitosync': 'cognito-sync',
    'configservice': 'config',
    'costandusagereportservice': 'cur',
    'costexplorer': 'ce',
    'databasemigrationservice': 'dms',
    'directoryservice': 'ds',
    'dynamodbstreams': 'dynamodb',
    'efs': 'elasticfilesystem',
    'elb': 'elasticloadbalancing',
    'elbv2': 'elasticloadbalancing',
    'emr': 'elasticmapreduce',
    'kinesisanalyticsv2': 'kinesisanalytics',
    'kinesisvideoarchivedmedia': 'kinesisvideo',
    'kinesisvideomedia': 'kinesisvideo',
    'lexmodelbuildingservice': 'lex',
    'lexruntimeservice':  'lex',
    'licensemanager':  'license-manager',
    'mediastoredata':  'mediastore',
    'migrationhub':  'mgh',
    'mturk':  'mechanicalturk',
    'neptune':  'neptune-db',
    'opsworkscm':  'opsworks-cm',
    'pinpoint':  'mobiletargeting',
    'pinpointemail':  'ses',
    'pinpointsmsvoice':  'sms-voice',
    'rdsdataservice':  'rds',
    'resourcegroups':  'resource-groups',
    's3control':  's3',
    'sagemakerruntime':  'sagemaker',
    'serverlessapplicationrepository':  'serverlessrepo',
    'sfn':  'states',
    'simpledb':  'sdb',
    'transcribeservice':  'transcribe',
    'wafregional':  'waf-regional',
}
