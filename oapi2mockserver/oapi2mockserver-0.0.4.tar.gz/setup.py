import setuptools

# load readme file
with open("README.md", "r") as fh:
    long_description = fh.read()

# load requirements (will be installed along with this package)
with open("requirements.txt", "r") as require:
    requirements = require.read()

# load subpackages which are provided to other users for import statements
with open("provides.txt", "r") as provide:
    provides = provide.read()

setuptools.setup(
    name="oapi2mockserver",
    version="0.0.4",
    author="allmyhomes GmbH",
    author_email="opensource@allmyhomes.com",
    description="Provides the basic setup of an API mockserver.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    packages=["oapi2mockserver"],

    install_requires=requirements,
    # package_data={'': ['<none_python_file_name>']},         # list all non python files
    # install_package_data=True,                              # installs non python files
    provides=[provides],                                      # usable by other users

    entry_points={
        "console_scripts": [                                  # create custom shell commands
            "oapi2mockserver = oapi2mockserver.main:main"             
        ]
    }
)
