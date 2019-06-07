import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="voximplant-apiclient",
    version="1.0.4",
    author="Voximplant",
    author_email="support@voximplant.com",
    description="Voximplant API client library",
    long_description=long_description,
#    long_description_content_type="text/markdown",
    url="https://voximplant.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "pytz",
        "pyjwt",
        "cryptography"
    ]
)