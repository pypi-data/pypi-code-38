import boto3


class Configuration:
    def __init__(self):
        self._secret_name = 'greg-test'
        self._region = 'us-east-1'

    @property
    def db_info(self):
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self._region
        )

        get_secret_value_response = client.get_secret_value(
            SecretId=self._secret_name
        )

        return get_secret_value_response['SecretString']
