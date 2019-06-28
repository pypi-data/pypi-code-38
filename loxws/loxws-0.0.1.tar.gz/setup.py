import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loxws",
    version="0.0.1",
    author="tjsmithuk",
    author_email="tsmith@clamfish.com",
    description="Loxone Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsmith/loxws",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pycryptodome>=3.8.1',
        'aiohttp>=3.5.4'
    ]
)