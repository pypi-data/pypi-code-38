from rockset.swagger_client.api import IntegrationsApi
from rockset.swagger_client.models import (
    AwsAccessKey,
    AwsRole,
    CreateIntegrationRequest,
    DynamodbIntegration,
    KinesisIntegration,
    GcpServiceAccount,
    GcsIntegration,
    RedshiftIntegration,
    S3Integration,
)


class IntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

        self.Dynamodb = DynamodbIntegrationClient(client)
        self.Gcs = GcsIntegrationClient(client)
        self.Kinesis = KinesisIntegrationClient(client)
        self.Redshift = RedshiftIntegrationClient(client)
        self.S3 = S3IntegrationClient(client)

    def list(self):
        return self.api.list().get('data')

    def get(self, name=None):
        return self.api.get(name).get('data')

    def delete(self, name=None):
        return self.api.delete(name).get('data')

    def retrieve(self, name=None):
        return self.get(name)

    def drop(self, name=None):
        return self.delete(name)


class DynamodbIntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

    def create(
        self,
        name=None,
        description=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    ):

        request = CreateIntegrationRequest(
            name=name,
            description=(description if description else ''),
            dynamodb=DynamodbIntegration(
                aws_access_key=AwsAccessKey(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                ),
            ),
        )

        return self.api.create(body=request).get('data')


class GcsIntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

    def create(
        self,
        name=None,
        description=None,
        service_account_key_file_json=None,
    ):

        request = CreateIntegrationRequest(
            name=name,
            description=(description if description else ''),
            gcs=GcsIntegration(
                gcp_service_account=GcpServiceAccount(
                    service_account_key_file_json=service_account_key_file_json,
                ),
            ),
        )

        return self.api.create(body=request).get('data')


class KinesisIntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

    def create(
        self,
        name=None,
        description=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_role_arn=None,
    ):
        if aws_role_arn:
            kinesis = KinesisIntegration(
                aws_role=AwsRole(aws_role_arn=aws_role_arn),
            )
        elif aws_access_key_id or aws_secret_access_key:
            kinesis = KinesisIntegration(
                aws_access_key=AwsAccessKey(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                ),
            )
        else:
            kinesis = None

        request = CreateIntegrationRequest(
            name=name,
            description=(description if description else ''),
            kinesis=kinesis,
        )

        return self.api.create(body=request).get('data')


class RedshiftIntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

    def create(
        self,
        name=None,
        description=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        username=None,
        password=None,
        host=None,
        port=None,
        s3_bucket_path=None,
    ):

        request = CreateIntegrationRequest(
            name=name,
            description=(description if description else ''),
            redshift=RedshiftIntegration(
                aws_access_key=AwsAccessKey(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                ),
                username=username,
                password=password,
                host=host,
                port=port,
                s3_bucket_path=s3_bucket_path,
            ),
        )

        return self.api.create(body=request).get('data')


class S3IntegrationClient(object):
    def __init__(self, client):
        self.api = IntegrationsApi(client)

    def create(
        self,
        name=None,
        description=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_role_arn=None,
    ):
        if aws_role_arn:
            s3 = S3Integration(aws_role=AwsRole(aws_role_arn=aws_role_arn))
        elif aws_access_key_id or aws_secret_access_key:
            s3 = S3Integration(
                aws_access_key=AwsAccessKey(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                ),
            )
        else:
            s3 = None

        request = CreateIntegrationRequest(
            name=name,
            description=(description if description else ''),
            s3=s3,
        )

        return self.api.create(body=request).get('data')
