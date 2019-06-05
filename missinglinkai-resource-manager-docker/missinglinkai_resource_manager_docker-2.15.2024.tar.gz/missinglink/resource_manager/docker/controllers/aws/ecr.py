import base64
import logging

import boto3

logger = logging.getLogger('ml-rmd.ecr')


class Ecr:
    @classmethod
    def login(cls, account, region, repo):
        logger.info('Authenticate: %s %s %s', account, region, repo)
        try:
            client = boto3.client('ecr', region_name=region)
            auth_data = client.get_authorization_token(registryIds=[account])['authorizationData'][0]
            user, token = base64.b64decode(auth_data['authorizationToken'].encode('utf-8')).decode('utf-8').split(':')
            return user, token, auth_data['proxyEndpoint']
        except Exception as ex:
            logger.warning('ECR Authentication: %s %s %s FAILED: %s', account, region, repo, str(ex))
            logger.debug('ECR Authentication: %s %s %s FAILED', account, region, repo, exc_info=1)
            return None, None, None
