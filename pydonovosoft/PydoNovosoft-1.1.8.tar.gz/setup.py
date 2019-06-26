import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PydoNovosoft",
    version="1.1.8",
    author="Mauricio Barrera",
    author_email="mauricio.barrerag@gmail.com",
    description="Some Python's utilities for other projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/donovosoft/PydoNovosoft",
    packages=setuptools.find_packages(),
    install_requires=[
          'protobuf',
          'pytz'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
