import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dsci_utils",
    version="0.0.15",
    author="Komodo Technologies, LLC",
    author_email="joe@ktechboston.com",
    description="A simple toolkit to assist with data science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ktechboston/db_utils",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'ujson',
        'beautifulsoup4',
        'numpy'
    ],
)
