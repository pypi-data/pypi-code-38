from setuptools import setup
import os

with open('README.md') as file:
    long_description = file.read()

tag = os.getenv("CIRCLE_TAG")
if tag:
    version = tag[1:]
else:
    version = "0.0.0development"

setup(
    name='stacklift',
    version=version,
    description='CloudFormation stack management tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/syginc/stacklift',
    scripts=['bin/stacklift'],
    author='syginc',
    license='MIT',
    keywords='aws cloudformation',
    packages=[
        "stacklift"
    ],
    python_requires='>=3.6',
    install_requires= [
        "pyyaml",
        "boto3",
        "click"
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools'
    ],
)
