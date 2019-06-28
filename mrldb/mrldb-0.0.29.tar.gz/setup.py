import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
##version#start##
__version__='0.0.29'
##version#end##
setuptools.setup(
    name="mrldb",
    version=__version__,
    author="Rémi 'Mr e-RL'LANGDORPH",
    author_email="r.langdorph@gmail.com",
    description="A library to handle your databases: cassandra, mariadb, (mysql), sqlite3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merlleu/mrldb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
