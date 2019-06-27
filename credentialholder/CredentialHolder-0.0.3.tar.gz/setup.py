import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CredentialHolder",
    version="0.0.3",
    author="brando",
    author_email="snoopy20704@capitalone.com",
    description="simple class for serializable and secure credential holder",
    install_requires=["pycryptodome"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bmpang/PythonCredentialHolderClass",
    packages=["credential_holder"],
    classifiers=["Programming Language :: Python :: 3"],
)
