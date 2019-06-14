import setuptools

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="sqlalchemy-migration-maker",
    version="0.1",
    author="Michael Pan",
    author_email="panmpan@gmail.com",

    python_requires='>=3.6',
    install_requires=['sqlalchemy'],

    description=("SQLAlachemy migration maker."
                 "Generate SQL command to auto migrate"),
    description_content_type="text/markdown",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/panmpan17/MigrationMaker",

    packages=setuptools.find_packages(exclude=["build", "dist", "docs",
                                               "*.egg-info", "testcase"]),
    keywords="sqlalchemy migration database db postgres python python3",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
