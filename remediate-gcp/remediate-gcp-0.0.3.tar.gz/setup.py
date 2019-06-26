from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="remediate-gcp",
    version="0.0.3",
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['google-api-python-client','google-auth'],
    python_requires='>=3',
    license='MIT',
    author='nottony',
    author_email='nottony-pypi@yahoo.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/asetiawan/siw99lc435',
    description='A collection of runbook to remediate GCP resources',
)
