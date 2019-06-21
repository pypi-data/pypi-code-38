from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Inomial Smile GraphQL Interface",
    version="1.0.4",
    classifiers=["Programming Language :: Python :: 3.7"],
    packages=["smileql"],
    install_requires=["requests", "gql", "zeep"],
    url="https://oss.rwts.com.au",
    author="Karl Kloppenborg",
    author_email="kkloppenborg@rwts.com.au",
    description="GraphQL Interface for Inomial Smile",
    long_description=long_description,
)
