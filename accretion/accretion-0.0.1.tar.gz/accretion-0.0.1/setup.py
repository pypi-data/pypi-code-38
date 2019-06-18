import sys
from setuptools import setup

args = ' '.join(sys.argv).strip()
if not any(args.endswith(suffix) for suffix in ['setup.py check -r -s', 'setup.py sdist']):
    raise ImportError('Did you mean to install accretion_cli?')

setup(
    author='Matt Bullock',
    author_email='m@ttsb42.com',
    classifiers=['Development Status :: 7 - Inactive'],
    description='Did you mean to install accretion_cli?',
    long_description='\nThis package has been parked by Matt Bullock to protect you against packages\nadopting names that might be common mistakes when looking for ours. You probably\nwanted to install accretion_cli. For more information, see https://accretion.readthedocs.io/en/stable/.',
    name='accretion',
    url='https://accretion.readthedocs.io/en/stable/',
    version='0.0.1'
)
