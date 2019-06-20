import time
from logging import Logger

from sidecar.const import Const


class AwsTagHelper:
    SpotFleetIdTag = "aws:ec2spot:fleet-request-id"
    AutoScalingGroupNameTag = "aws:autoscaling:groupName"
    MAX_TAG_ATTEMPTS = 30

    @staticmethod
    def wait_for_tags(resource, logger: Logger) -> {}:
        if not resource.tags:
            resource.reload()

        for attempt in range(AwsTagHelper.MAX_TAG_ATTEMPTS):
            if resource.tags:
                return {tag['Key']: tag['Value'] for tag in resource.tags}

            logger.warning(f'Could not get tags (attempt {attempt} of {AwsTagHelper.MAX_TAG_ATTEMPTS}). Retrying in 5 sec.')
            time.sleep(5)
            resource.reload()

        logger.error(f'Could not get tags from "{resource.id}"')

    @staticmethod
    def wait_for_tag(resource, tag_name: str, logger: Logger) -> str:
        tags = {}
        if not resource.tags:
            resource.reload()

        for attempt in range(AwsTagHelper.MAX_TAG_ATTEMPTS):
            tags = {x['Key']: x['Value'] for x in resource.tags or {}}
            if tag_name in tags:
                return tags[tag_name]

            logger.warning(f'Could not get tag "{tag_name}" (attempt {attempt} of {AwsTagHelper.MAX_TAG_ATTEMPTS}). Retrying in 5 sec.')
            time.sleep(5)
            resource.reload()

        logger.error(f'Could not get tag "{tag_name}" from "{resource.id}". \n'
                     f'Existing tags ({len(tags)}): \n'
                     '\n'.join([f'{k}={v}' for k, v in tags.items()]))

    @staticmethod
    def create_tag(key, value):
        return {'Key': key, 'Value': value}

    @staticmethod
    def parse_apps_status_tag_value(apps_status_value: str) -> {}:
        app_to_status_map = dict()
        if apps_status_value:
            all_statuses = apps_status_value.split(Const.CSV_TAG_VALUE_SEPARATE)
            app_to_status_map = dict(state.split(Const.APP_STATE_KEY_VALUE_SEPARATOR) for state in all_statuses)
        return app_to_status_map

    @staticmethod
    def format_apps_status_tag_value(app_to_status_map: {}) -> str:
        return Const.CSV_TAG_VALUE_SEPARATE.join(
            ["{KEY}{SEP}{VALUE}".format(KEY=app_name, SEP=Const.APP_STATE_KEY_VALUE_SEPARATOR, VALUE=app_status)
             for app_name, app_status in app_to_status_map.items()])
