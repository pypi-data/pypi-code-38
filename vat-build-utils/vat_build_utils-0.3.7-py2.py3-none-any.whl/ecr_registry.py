import base64

import boto3
from botocore.exceptions import ClientError
import docker

from build_utils import docker_utils

class EcrRegistry(object):
    def __init__(self, config):
        self.host = config['host']
        self.repositories = config.get('repositories', {})
        self.registry_id = self.host.split('.')[0]

    def get_full_image_tag(self, image_name, tag):
        return "{0}:{1}".format(self._get_image_repository_uri(image_name), tag)

    def has_image(self, image_name, tag):
        ecr_client = boto3.client('ecr')

        try:
            ecr_client.describe_images(
                registryId=self.registry_id,
                repositoryName=self._get_image_repository_name(image_name),
                imageIds=[{'imageTag': tag}]
            )
            return True

        except ClientError as ex:
            if ex.response['Error']['Code'] == 'ImageNotFoundException':
                return False
            else:
                raise ex

    def push_image(self, image_name, tag):
        docker_client = docker.from_env(version='auto')
        docker_utils.push_docker_image(
            docker_client.api,
            repository=self._get_image_repository_uri(image_name),
            tag=tag,
            auth_config=self._get_auth_config()
        )

    def pull_image(self, image_name, tag):
        docker_client = docker.from_env(version='auto')
        docker_client.api.pull(
            repository=self._get_image_repository_uri(image_name),
            tag=tag,
            auth_config=self._get_auth_config()
        )
        return self.get_full_image_tag(image_name, tag)

    def _get_image_repository_name(self, image_name):
        return self.repositories[image_name]

    def _get_image_repository_uri(self, image_name):
        return "{0}/{1}".format(self.host, self._get_image_repository_name(image_name))

    def _get_auth_config(self):
        ecr_client = boto3.client('ecr')

        token_response = ecr_client.get_authorization_token(registryIds=[self.registry_id])
        username, password = base64.b64decode(
            token_response['authorizationData'][0]['authorizationToken']).decode('utf-8').split(':')

        return {
            'username': username,
            'password': password
        }
