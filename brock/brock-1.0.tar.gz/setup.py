from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='brock',
    version='1.0',
    author='Ben Fortuna',
    author_email='fortuna@micronode.com',
    description='A collection of Terraform-based blueprints',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/micronode/bedrock',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bmt = bedrock.manifest:main',
            'bbt = bedrock.blueprint:main',
        ]
    }
)
