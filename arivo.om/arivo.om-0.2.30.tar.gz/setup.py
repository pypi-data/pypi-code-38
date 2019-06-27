from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


def line(f):
    return f.readline().replace("\n", "").strip()


with open(path.join(here, "pip", "VERSION")) as f:
    VERSION = line(f)

with open(path.join(here, "pip", "BUILD_INFO")) as f:
    GIT_BRANCH = line(f)
    GIT_COMMIT = line(f)
    GIT_COMMIT_SHORT = line(f)

setup(
    name='arivo.om',
    version='{}'.format(VERSION),
    license="GPL-3",
    description='Util functions for om docker containers',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    long_description="VERSION={}\n"
                     "GIT_BRANCH={}\n"
                     "GIT_COMMIT={}\n"
                     "GIT_COMMIT_SHORT={}".format(VERSION, GIT_BRANCH, GIT_COMMIT, GIT_COMMIT_SHORT),

    packages=find_packages(exclude=["om.utils.test", "om.message.test"]),
    install_requires=[
        'six',
        'related',
        "enum34; python_version < '3.0'",
        'editdistance',
        'sentry_sdk',
        'pyyaml',
        'pyzmq'
    ]
)
