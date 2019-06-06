import setuptools


long_description = "Utility for bulk loading pandas dataframes into databases"

setuptools.setup(
    name="data_catapult",
    version="0.0.20",
    author="Jonathan Speiser",
    author_email="jonathan@datawheel.us",
    description="Python bulk data loading ETL library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Datawheel/catapult",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "clickhouse-driver==0.0.19",
        "sqlalchemy==1.2.10",
        "psycopg2==2.7.5",
        "pyyaml",
        "dw-python-monetdb-async",
        "pandas==0.24.2",
        "requests"
    ]
)
