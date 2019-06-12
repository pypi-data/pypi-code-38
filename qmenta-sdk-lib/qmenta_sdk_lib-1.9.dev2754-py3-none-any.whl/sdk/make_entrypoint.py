import sys
from argparse import ArgumentParser

entry_point_contents = '''#!/bin/bash -exu
export PYTHONPATH="${{PYTHONPATH:+$PYTHONPATH:}}{tool_path}"

# Add your configuration here:
# ...

# Tool start:
exec {executable} -m qmenta.sdk.executor "$@"
'''


def make_entrypoint():
    parser = ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('tool_paths', nargs='+')
    options = parser.parse_args()

    with open(options.target, 'w') as fp:
        fp.write(entry_point_contents.format(
            executable=sys.executable,
            tool_path=":".join(options.tool_paths)
        ))


if __name__ == '__main__':
    make_entrypoint()
