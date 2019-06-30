from setuptools import setup, find_packages
from os.path import join, dirname
import stereo7.version

setup(
    name='stereo7',
    version=stereo7.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'google-api-python-client',
        'oauth2client',
        'httplib2',
        'pillow',
        'slackclient'
    ],
    entry_points={
        'console_scripts':
            ['stereo7 = stereo7.core:console']
    },
    test_suite='tests'
)
