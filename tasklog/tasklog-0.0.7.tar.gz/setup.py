""" Setup script for the import application.

"""
from os import walk
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


def project_description():
    description = ""

    with open("README.md", "r") as fh:
        description += fh.read()

    with open("config/config.yml", "r") as fh:
        description += "\n\n Sample Config file:  \n\n " \
                       "```yaml \n\n{}\n\n```".format(fh.read())

    with open("tests/tasklog/operations/submit/tasklogs_success.txt", "r") as fh:
        description += "\n\n Sample tasklog file:  \n\n " \
                       "```{}```".format(fh.read())

    return description


with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

_config = {
    "name": "tasklog",
    "author": "David Andreoletti",
    "author_email": "david.andreoletti.dev@gmail.com",
    "python_requires": ">=3.7.3",
    "url": "https://github.com/davidandreoletti/tasklog-cli",
    "description": "CLI to submit tasklogs to Jira",
    "long_description": project_description(),
    "long_description_content_type": "text/markdown",
    "package_dir": {"": "src"},
    "packages": find_packages("src"),
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    "entry_points": {
        "console_scripts": ("tasklog = tasklog.__main__:main"),
    },
    "data_files": [],
    "install_requires": install_requires,
}


def main():
    """ Execute the setup command.

    """

    def data_files(*paths):
        """ Expand path contents for the `data_files` config variable.  """
        for path in map(Path, paths):
            if path.is_dir():
                for root, _, files in walk(str(path)):
                    yield root, tuple(str(Path(root, name)) for name in files)
            else:
                yield str(path.parent), (str(path),)
        return

    def version():
        """ Get the local package version. """
        namespace = {}
        path = Path("src", _config["name"], "__version__.py")
        exec(path.read_text(), namespace)
        return namespace["__version__"]

    _config.update({
        "data_files": list(data_files(*_config["data_files"])),
        "version": version(),
    })
    setup(**_config)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
