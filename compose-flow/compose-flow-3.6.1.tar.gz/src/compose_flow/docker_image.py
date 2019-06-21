import re
from typing import Callable

import semver

from compose_flow.errors import PublishMajorMinorTagsError


OFFICIAL_RELEASE_REGEX = re.compile(r'^\d+\.\d+\.\d+$')


class DockerImage:

    def __init__(self, tagged_image_name: str = None, publish_callable: Callable = None, tag_callable: Callable = None):
        """
        Init method
        :param tagged_image_name: A fully qualified image name of format repository/image_name:tag
        :param publish_callable: A callable that accepts a fully qualified image name as its only argument
                    and publishes it
        :param tag_callable: A callable that accepts fully qualified image names as arguments and tags the image
                referenced by the first string with the second string
        """
        self._tagged_image_name = tagged_image_name
        self._parse_tagged_image_name()

        self._publish_callable = publish_callable
        self._tag_callable = tag_callable

    @property
    def official_release(self) -> bool:
        """Return whether or not we can publish with auto tags."""
        return bool(OFFICIAL_RELEASE_REGEX.match(self.tag))

    def _get_tagged_image_name(self, tag: str = None):
        """Utility for getting a tagged image name"""
        tag = tag or self.tag
        return f'{self.repository}/{self.name}:{tag}'

    def _parse_tagged_image_name(self):
        """
        Parse the tagged_image_name and set repository, image_name, semver version_info
        :return:
        """
        self.repository = self._tagged_image_name.split('/')[0] if '/' in self._tagged_image_name else None
        self.tag = self._tagged_image_name.split(':')[1] if ':' in self._tagged_image_name else None
        self.name = re.match(rf'{self.repository}/(.*):{self.tag}', self._tagged_image_name).group(1)
        try:
            self.version_info = semver.VersionInfo.parse(self.tag)
        except ValueError:
            self.version_info = None

    def publish_with_major_minor_tags(self):
        """Publish an image and auto-tag major and minor releases"""
        if self.official_release:
            self.publish()
            self._publish_major()
            self._publish_minor()
        else:
            raise PublishMajorMinorTagsError(
                    f'Publishing with auto tags is only allowed for official release MAJOR.MINOR.PATCH tags.'
                    f'Current tag: {self.version_info}'
            )

    def publish(self):
        """Publish the private image"""
        self._publish(self.version_info)

    def _publish(self, tag: str):
        tagged_image_name = self._get_tagged_image_name(tag)
        self._publish_callable(tagged_image_name)

    def _publish_major(self):
        """Publish image tagged to major version"""
        tag = self.version_info.major
        self._add_tag_to_image(tag)
        self._publish(tag)

    def _publish_minor(self):
        """Publish image tagged to major.minor version"""
        tag = f'{self.version_info.major}.{self.version_info.minor}'
        self._add_tag_to_image(tag)
        self._publish(tag)

    def _add_tag_to_image(self, tag: str):
        """Tag the private image with a new tag"""
        tagged_image_name = self._get_tagged_image_name(tag)
        self._tag_callable(self._tagged_image_name, tagged_image_name)

    def __str__(self):
        return self._get_tagged_image_name()

    def __repr__(self):
        return self._get_tagged_image_name()
