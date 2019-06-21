import argparse
from typing import List

from compose_flow.docker_image import DockerImage

from .base import BaseBuildSubcommand


class Publish(BaseBuildSubcommand):
    """
    Subcommand for building and pushing Docker images
    """

    @classmethod
    def fill_subparser(cls, parser, subparser):
        subparser.epilog = __doc__
        subparser.formatter_class = argparse.RawDescriptionHelpFormatter

        subparser.add_argument(
            '--tag-major-minor',
            default=False,
            action='store_true',
            help='automatically publish major and major.minor tags pointing to the new docker image',
        )

    def get_built_tagged_image_names(self) -> List[str]:
        """Return a list of built tagged image names"""
        docker_images = set()

        profile = self.workflow.profile
        for service_data in profile.data['services'].values():
            if service_data.get('build'):
                tagged_image_name = service_data.get('image')
                docker_images.add(tagged_image_name)

        return list(docker_images)

    def get_built_docker_images(self) -> List[DockerImage]:
        """
        Returns a list of docker images built in the compose file
        """
        tagged_image_names = self.get_built_tagged_image_names()
        docker_images = [
            DockerImage(
                tagged_image_name=tagged_image_name,
                publish_callable=self.execute_publish,
                tag_callable=self.execute_tag,
            )
            for tagged_image_name in tagged_image_names
        ]
        return docker_images

    def push(self):
        docker_images = self.get_built_docker_images()
        for docker_image in docker_images:
            if len(docker_images) > 1:
                self.logger.info(f'pushing {docker_image}')

            if self.workflow.args.dry_run:
                self.logger.info(f'docker push {docker_image}')
            elif self.workflow.args.tag_major_minor:
                docker_image.publish_with_major_minor_tags()
            else:
                docker_image.publish()

    def execute_publish(self, tagged_image_name: str):
        self.execute(f'docker push {tagged_image_name}', _fg=True)

    def execute_tag(self, original, new):
        self.execute(f'docker tag {original} {new}')

    def handle(self):
        self.build(pull=False)

        self.push()
