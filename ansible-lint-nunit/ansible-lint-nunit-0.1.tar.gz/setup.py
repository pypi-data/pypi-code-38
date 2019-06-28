from setuptools import setup

from bootstrap import bootstrap

version = bootstrap.version()

setup(
    name='ansible-lint-nunit',
    packages=['bootstrap'],
    version=version,
    description='ansible-lint to NUnit converter.',
    author='wasil',
    author_email='ferhat.yildiz@turingts.com',
    url='https://github.com/ferhaty/ansible-lint-nunit',
    download_url='https://github.com/ferhaty/ansible-lint-nunit/archive/%s.tar.gz' % (version),
    keywords=['ansible', 'nunit'],
    classifiers=[],
    entry_points={
        "console_scripts": ['ansible-lint-nunit = bootstrap.bootstrap:main']
    },
    install_requires=[
        'ansible-lint',
    ],
)
