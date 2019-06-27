import os
import shutil

import cc_core.agent.blue.__main__

from cc_agency.commons.helper import calculate_agency_id


def build_dir_path(conf):
    agency_id = calculate_agency_id(conf)
    return os.path.expanduser(os.path.join('~', '.cache', agency_id, 'build'))


def init_build_dir(conf):
    build_dir = build_dir_path(conf)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    shutil.copy(cc_core.agent.blue.__main__.__file__, os.path.join(build_dir, 'blue_agent.py'))

    content = [
        'FROM docker.io/debian:9.5-slim',
        'RUN useradd -ms /bin/bash cc',
        'ADD --chown=cc:cc ./blue_agent.py /cc/blue_agent.py'
    ]
    with open(os.path.join(build_dir, 'Dockerfile'), 'w') as f:
        for line in content:
            print(line, file=f)
