import json
import os
from tempfile import NamedTemporaryFile

import delegator

import pytest

STORYSCRIPT_CONFIG = {
    'id': os.environ['STORYSCRIPT_INT_CONF_USER_ID'],
    'access_token': os.environ['STORYSCRIPT_INT_CONF_ACCESS_TOKEN']
}


@pytest.fixture
def cli():
    def function(*args, logged_in=True):

        tf = NamedTemporaryFile().name

        if logged_in:
            # Create a temporary config file.
            with open(tf, 'w') as f:
                f.write(json.dumps(STORYSCRIPT_CONFIG))

        # Make temporary file.
        args = ' '.join(args)
        c = delegator.run(f'story {args}', env={'STORY_CONFIG_PATH': tf})

        os.remove(tf)
        return c

    return function


@pytest.fixture
def app_dir():
    pass
