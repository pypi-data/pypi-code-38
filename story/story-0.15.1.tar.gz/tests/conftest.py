import os
from tempfile import NamedTemporaryFile

import pytest
import delegator

# TODO: env vars
STORYSCRIPT_CONFIG = """{
   "id":"cd3fb9d0-fc54-48c5-9a1a-9daead7da490",
   "access_token":"vmlLTkC+Q5lBJ0XU/OHVWA==",
   "name":null,
   "email":"kenneth+tests@storyscript.io",
   "username":"storyscript-cli-test",
   "beta":true
}""".strip()


@pytest.fixture
def cli():
    def function(*args, logged_in=True):

        tf = NamedTemporaryFile().name

        if logged_in:
            # Create a temporary config file.
            with open(tf, 'w') as f:
                f.write(STORYSCRIPT_CONFIG)

        # Make temporary file.
        args = ' '.join(args)
        c = delegator.run(f'story {args}', env={"STORY_CONFIG_PATH": tf})

        os.remove(tf)
        return c

    return function


@pytest.fixture
def app_dir():
    pass
