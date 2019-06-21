import setuptools

with open("Read.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="root_pack",
    version="1.1.1",
    author="Jincy Baby",
    author_email="jincybaby@icfoss.org",
    description="Extract root from a Malayalam word",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/icfoss/Malayalam-Computing/Root_Extractor_for_Malayalam",
    packages=setuptools.find_packages(),
    license='GNU Public License',
    package_data = {
        '': ['*.txt', '*.csv'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)