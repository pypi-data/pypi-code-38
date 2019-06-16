"""Main code that runs when mam is used from the console."""

import json
import os.path
import subprocess  # nosa: bandit[B404]
import tempfile
from typing import Any, List

import yaml  # nosa: pylint[E0401]

from ._mam import find, find_system
from ._mam.core.configs import load
from ._mam.core.objects import Message


def main() -> None:
    """Run MAM."""
    runner = find_system('@mam/runner.py')
    cwd = os.getcwd()
    env = os.path.join(cwd, '.mam')
    try:
        os.mkdir('.mam/')
    except FileExistsError:
        pass
    try:
        os.mkdir('.mam/_build/')
    except FileExistsError:
        pass

    config = load('./configs/mam.yaml')
    with open('./configs/_mam.yaml', 'w') as config_output:
        yaml.safe_dump(config, config_output)

    # return
    with tempfile.TemporaryDirectory(dir='.mam/_build/') as name:
        subprocess.run([  # nosa: bandit[B607,B603]
            'nox',
            '--noxfile', runner.path or '',
            '--envdir', env,
            '-r',
            '--',
            name,
        ])

        data: List[Any] = []
        for path in os.listdir(name):
            with open(os.path.join(name, path)) as file_object:
                data.extend(json.load(file_object))
        data = [Message.from_dict(m) for m in data]

        # nosa: pylint[:.obj is not callable]
        for mutation in config.get('mutations', None) or []:
            data = find(mutation).obj(data)

        output_function = config.get('output', '@mam.output:default')
        find(output_function).obj(data)


if __name__ == '__main__':
    main()
