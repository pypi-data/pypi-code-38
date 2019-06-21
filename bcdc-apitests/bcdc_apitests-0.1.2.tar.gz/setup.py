'''
Created on Jun. 6, 2019

@author: KJNETHER

using date as versions to simplify
'''
import setuptools
import datetime
import version

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requires = f.read().splitlines()
    print 'requirements:', requires


setuptools.setup(
    name="bcdc_apitests",
    # version=datetime.datetime.now().strftime('%Y.%m.%d'),
    version=version.next_version,
    author="Kevin Netherton",
    author_email="kevin.netherton@gov.bc.ca",
    description="API testing for BC Data Catalog",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bcgov/bcdc-test",
    packages=setuptools.find_packages(),
    python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=requires,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Testing",
        "Operating System :: OS Independent",
    ],
)
