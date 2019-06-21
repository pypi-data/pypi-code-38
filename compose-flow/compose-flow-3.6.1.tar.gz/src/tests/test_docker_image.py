import json
from unittest import TestCase, mock

import semver

from compose_flow.errors import PublishMajorMinorTagsError
from compose_flow.docker_image import DockerImage
from tests.utils import get_content


class DockerImageTestMixin:
    _default_repository = 'my-registry.foobar.org'
    _default_image_name = 'tompose-flow'
    _default_tag = '3.5.9'
    _default_tagged_image_name = f'{_default_repository}/{_default_image_name}:{_default_tag}'

    def _get_docker_image(self, tagged_image_name: str = None):
        """
        Return a private image instance
        """
        tagged_image_name = tagged_image_name or self._default_tagged_image_name
        return DockerImage(tagged_image_name=tagged_image_name, publish_callable=mock.MagicMock(),
                           tag_callable=mock.MagicMock())


class DockerImageHappyPathTestCase(DockerImageTestMixin, TestCase):

    @mock.patch('compose_flow.commands.subcommands.base.BaseSubcommand.execute')
    def test_e2e_publish_auto_tags(self, *mocks):
        """
        Test that we can publish and auto-tag an image.
        """
        docker_image = self._get_docker_image()
        docker_image.publish_with_major_minor_tags()

        major_tagged_image_name = f'{self._default_repository}/{self._default_image_name}:3'
        minor_tagged_image_name = f'{self._default_repository}/{self._default_image_name}:3.5'
        target_publish_call_args = [
            (self._default_tagged_image_name),
            (major_tagged_image_name),
            (minor_tagged_image_name),
        ]
        publish_callable_mock = docker_image._publish_callable
        for call_args in target_publish_call_args:
            publish_callable_mock.assert_any_call(call_args)

        target_tag_call_args = [
            (self._default_tagged_image_name, major_tagged_image_name),
            (self._default_tagged_image_name, minor_tagged_image_name),
        ]
        tag_callable_mock = docker_image._tag_callable
        for call_args in target_tag_call_args:
            tag_callable_mock.assert_any_call(*call_args)

    def test_ut_image_name(self, *mocks):
        """Ensure DockerImage populates name."""
        docker_image = self._get_docker_image()
        self.assertEqual(self._default_image_name, docker_image.name)

    def test_ut_repository(self, *mocks):
        """Ensure DockerImage populates repository."""
        docker_image = self._get_docker_image()
        self.assertEqual(self._default_repository, docker_image.repository)

    def test_ut_tag_version_info(self, *mocks):
        """Ensure DockerImage populates tag_version_info"""
        docker_image = self._get_docker_image()
        target_version_info = semver.VersionInfo.parse(self._default_tag)
        self.assertEqual(target_version_info, docker_image.version_info)

    def test_ut_official_release(self, *mocks):
        """
        Ensure official release property happy path works.
        """
        docker_image = self._get_docker_image()
        self.assertEqual(True, docker_image.official_release)

    def test_ut_publish(self, *mocks):
        """Ensure `publish` publishes the original private image"""
        docker_image = self._get_docker_image()
        docker_image.publish()
        self.assertEqual(
            docker_image._publish_callable.call_args[0][0],
            docker_image._get_tagged_image_name(self._default_tag)
        )

    def test_ut_publish_major(self, *mocks):
        """Ensure `publish_major` tags and publishes desired tag"""
        docker_image = self._get_docker_image()
        docker_image._publish_major()
        target_tagged_image_name = f'{self._default_repository}/{self._default_image_name}:3'
        docker_image._tag_callable.assert_any_call(*(self._default_tagged_image_name, target_tagged_image_name))
        docker_image._publish_callable.assert_any_call(target_tagged_image_name)

    def test_ut_publish_minor(self, *mocks):
        """Ensure `publish_minor` tags and publishes desired tag"""
        docker_image = self._get_docker_image()
        docker_image._publish_minor()
        target_tagged_image_name = f'{self._default_repository}/{self._default_image_name}:3.5'
        docker_image._tag_callable.assert_any_call(*(self._default_tagged_image_name, target_tagged_image_name))
        docker_image._publish_callable.assert_any_call(target_tagged_image_name)

    def test_ut_official_release_0_in_version(self, *mocks):
        """Ensure official_release happy path works with releases containing a 0"""
        tagged_image_name = f'{self._default_repository}/{self._default_image_name}:1.0.1'
        docker_image = self._get_docker_image(tagged_image_name)
        self.assertEqual(True, docker_image.official_release)


class DockerImageSadPathTestCase(DockerImageTestMixin, TestCase):

    def test_e2e_invalid_publish_with_auto_tags(self, *mocks):
        """Ensure unhappy path works as we expect"""
        bad_tag = '2.0.3-999-385uegfd-feature--21345-foo-bar-baz'
        invalid_tagged_image_name = f'{self._default_repository}/{self._default_image_name}:{bad_tag}'
        docker_image = self._get_docker_image(invalid_tagged_image_name)
        with self.assertRaises(PublishMajorMinorTagsError):
            docker_image.publish_with_major_minor_tags()
