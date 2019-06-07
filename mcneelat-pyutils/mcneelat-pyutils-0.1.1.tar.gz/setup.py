from setuptools import find_packages, setup

# The text of the README file
with open("README.md") as file:
    README = file.readlines()

# This call to setup() does all the work
setup(
    name="mcneelat-pyutils",
    version="0.1.1",
    description="A collection of helpful Python utilities to simplify dealing with databases, Kafka, and more.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tommym89/pyutils",
    author="Tommy McNeela",
    author_email="mcneelat@gmail.com",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["kafka-python", "psycopg2-binary", "requests"],
)
