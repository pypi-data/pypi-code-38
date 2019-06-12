import os
from unittest import TestCase

import docker
from docker.errors import ContainerError


class PipeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.image_tag = 'bitbucketpipelines/demo-pipe-python:ci' + \
            os.getenv('BITBUCKET_BUILD_NUMBER', 'local')
        cls.docker_client = docker.from_env()
        cls.docker_client.images.build(
            path='.', tag=cls.image_tag)

    def run_and_get_container(self, cmd=None, **kwargs):
        # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
        cwd = os.getcwd()
        try:
            return self.docker_client.containers.run(
                self.image_tag,
                command=cmd,
                volumes={cwd: {'bind': cwd, 'mode': 'rw'}},
                working_dir=cwd,
                detach=True,
                **kwargs
            )
        except ContainerError as e:
            return e.container

    def run_container(self, cmd=None, **kwargs):
        container = self.run_and_get_container(cmd, **kwargs)
        container.wait()

        return container.logs().decode()


class PipeTestCaseTestCase(PipeTestCase):

    @classmethod
    def setUpClass(cls):
        with open('Dockerfile', 'w') as f:
            f.write("FROM python:3.7")
        super().setUpClass()

    def test_the_test(self):
        result = self.run_container('echo hello world')
        self.assertIn(b'hello world', result)
