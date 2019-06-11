import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flanks",
    version="0.0.3",
    author="Flanks Team",
    author_email="hello@flanks.io",
    description="Small client for FlanksAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flanks-io/python-flanks",
    install_requires=[
        'requests >= 2.20; python_version >= "3.0"',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)