import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="visualise-spacy-pattern",
    version="0.0.1",
    author="Nicholas Morley",
    author_email="nick.morley111@gmail.com",
    description=" Visualise spacy dependency patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyclecycle/visualise-spacy-pattern",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
