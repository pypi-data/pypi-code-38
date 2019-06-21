import logging
import os

from .utils import remerge, yaml_dump, yaml_load


def get_overlay_filenames(overlay):
    logger = logging.getLogger('get_overlay_filenames')

    overlay_filenames = []

    applied = []
    for item in overlay:
        if item in applied:
            continue

        applied.append(item)

        path = None
        if isinstance(item, dict):
            name = item['name']
            path = item['path']
        else:
            name = item

        # join path and name if the path is given
        if path:
            _filename = os.path.join(path, name)
        else:
            _filename = name

        if _filename and os.path.exists(_filename) and os.path.isfile(_filename):
            overlay_filenames.append(_filename)
        else:
            # prefix partial with a dot in order to complete the name
            if name:
                name = '.{}'.format(name)
            else:
                name = ''

            _filename = 'docker-compose{}.yml'.format(name)
            if path:
                _filename = os.path.join(path, _filename)

            logging.debug('_filename={}'.format(_filename))

            if os.path.exists(_filename):
                overlay_filenames.append(_filename)
            else:
                logger.warning(f'filename={_filename} does not exist, skipping')

    # check to see if any filenames were found, else default to docker-compose.yml
    if not overlay_filenames:
        overlay_filenames.append('docker-compose.yml')

    return overlay_filenames


def merge_profile(profile: dict) -> str:
    """
    Returns the merged compose file contents

    Args:
        profile: the profile data to merge
    """
    filenames = get_overlay_filenames(profile)

    # merge multiple files together so that deploying stacks works
    # https://github.com/moby/moby/issues/30127
    if len(filenames) > 1:
        yaml_contents = []

        for item in filenames:
            with open(item, 'r') as fh:
                yaml_contents.append(yaml_load(fh))

        merged = remerge(yaml_contents)
        content = yaml_dump(merged)
    else:
        try:
            with open(filenames[0], 'r') as fh:
                content = fh.read()
        except FileNotFoundError:
            content = ''

    return content
