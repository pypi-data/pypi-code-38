from distutils.core import setup

import cognite_uploader

setup(
    # Application name:
    name="cognite-uploader",

    # Version number (initial):
    version=cognite_uploader.__version__,

    # Application author details:
    author="Sondre Sortland",
    author_email="sondre.sortland@cognite.com",

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/cognitedata/python-uploader",

    packages=['cognite_uploader'],

    description="Uploader used in extractors.",

    # Dependent packages (distributions)
    install_requires=[
        "cognite-sdk",
    ],
)
