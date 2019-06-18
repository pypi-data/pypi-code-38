import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="b2-storage",
    version="0.0.1",
    author="Royendgel Silbere",
    author_email="rsilberie@techprocur.com",
    description="Backblaze b2 ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/royendgel/b2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
