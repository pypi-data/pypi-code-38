import sys
from argparse import ArgumentParser

entry_point_contents = '''#!/bin/bash -eu
# Add your configuration here:
# ...

# Tool start:
exec {executable} -m qmenta.sdk.executor "$@"
'''


def make_entrypoint():

    parser = ArgumentParser()
    parser.add_argument('target')
    options = parser.parse_args()

    with open(options.target, 'w') as fp:
        fp.write(entry_point_contents.format(
            executable=sys.executable
        ))


if __name__ == '__main__':
    make_entrypoint()
