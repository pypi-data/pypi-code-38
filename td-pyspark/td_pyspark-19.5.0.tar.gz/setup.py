import re
import ast
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('td_pyspark/version.py', 'rb') as f:
    version_re = re.compile(r'__version__\s+=\s+(.*)')
    VERSION = str(ast.literal_eval(version_re.search(f.read().decode('utf-8')).group(1)))

setuptools.setup(
    name="td_pyspark",
    version=VERSION,
    description="Treasure Data extension for pyspark",
    author="Arm Treasure Data",
    author_email="dev+pypi@treasure-data.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://support.treasuredata.com/hc/en-us/sections/360000317028-Data-Science-and-SQL-Tools",
    packages=setuptools.find_packages(),
    license="Apache 2",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='Spark PySpark TreasureData',
    extras_require={
        'spark': ['pyspark>=2.4.0']
    }
)
