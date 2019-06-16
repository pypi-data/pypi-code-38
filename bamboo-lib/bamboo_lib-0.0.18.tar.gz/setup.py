import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as vfh:
    version = vfh.read()

setuptools.setup(
    author="Jonathan Speiser",
    author_email="jonathan@datawheel.us",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    description="Python ETL library",
    install_requires=[
        "pandas==0.23.3",
        "sqlalchemy==1.2.10",
        "data-catapult",
        "paramiko==2.4.1",
        "sshtunnel==0.1.4",
        "redis==2.10.6",
        "pytest"
    ],
    name="bamboo_lib",
    license='All Rights Reserved',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    version=version,
    url="https://github.com/Datawheel/bamboo-lib",
)
