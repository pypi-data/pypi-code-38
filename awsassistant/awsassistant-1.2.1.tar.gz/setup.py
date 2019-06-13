from setuptools import setup


version = "1.2.1"

long_descr = "This is awshelper develope for \
    developer to easy develope aws services"


setup(
    name="awsassistant",
    packages=["Services", "Services.cloudwatch", "Services.display"],
    entry_points={
        "console_scripts": ['awsassistant = Services.awshelper:main']
    },
    version=version,
    description="Python command line application to help us with aws api",
    long_description=long_descr,
    author="devesh bajaj",
    author_email="deveshbajaj59@gmail.com",
    install_requires=[
        'pytz', 'prettytable', 'colorama', 'boto3'
    ],
)
