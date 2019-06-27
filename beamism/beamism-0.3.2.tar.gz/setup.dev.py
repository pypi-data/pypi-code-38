# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup, find_packages
import git


def _requires_from_file(filename):
    return open(filename).read().splitlines()


try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


try:
    current_commit_number = git.Repo(search_parent_directories=True).head.object.count() + 1
    zero_padding = '%03d' % current_commit_number
    version = '.'.join(list(zero_padding))
    with open('version.cache', 'w') as f:
        f.write(version)
except git.exc.InvalidGitRepositoryError:
    # Dataflow Deploy時、.gitフォルダはアップロードされないため、gitの情報をバージョンに利用できない。そのため、version.cacheからversion情報を取得する
    with open('version.cache', 'r') as f:
        version = f.read()


setup(
    name="beamism",
    version=version,
    packages=find_packages(),
    description='welcome to beamism',
    long_description=readme,
    platforms='Linux, Darwin',
    zip_safe=False,
    include_package_data=True,
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)
