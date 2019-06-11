from setuptools import setup
import os

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

setup(
    name='micropipes-worker',
    version=version,
    description='Micropipes worker package',
    author='Richard Holly',
    author_email='richard.holly@optimaideas.com',
    license='Commercial',
    install_requires=["jsonschema>=3.0.1", "pika>=1.0.0"],
    packages=['shared', 'worker'],
    url='https://gitlab.com/aicu/lab/aicu_micropipes',
    zip_safe=False
)