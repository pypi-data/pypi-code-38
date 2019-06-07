import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloakensdk",
    version="0.0.4",
    author="Aaron Jonen",
    author_email="ajonen@mailcan.com",
    description="SDK for use with Cloaken url unshortener AMI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/guzzijob/cloakensdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "requests-futures",
        "urllib3"

        ],
)
