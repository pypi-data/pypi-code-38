from setuptools import setup

setup(
    name='bitbucket-pipes-toolkit',
    version='0.7.0',
    packages=['bitbucket_pipes_toolkit', ],
    url='https://bitbucket.org/bitbucketpipelines/pipes-tools-python/src',
    author='Atlassian',
    author_email='bitbucketci-team@atlassian.com',
    description='This package containes various helpers for developing bitbucket pipelines pipes',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=['colorama==0.3.9',
                      'colorlog==4.0.2',
                      'pyyaml==5.1',
                      'Cerberus==1.2',
                      'docker==3.7.0']
)
