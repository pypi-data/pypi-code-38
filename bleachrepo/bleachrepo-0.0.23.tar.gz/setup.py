import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = required = f.read().splitlines()

setuptools.setup(
    name="bleachrepo",
    version="0.0.23",
    author="Amir Moualem",
    author_email="amoualem@gmail.com",
    description="Find and remove the mold from your source control repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shesekino/bleach",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=install_requires,
)
