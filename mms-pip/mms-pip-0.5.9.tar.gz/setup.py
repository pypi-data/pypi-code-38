import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

required_packages=[
    'google-cloud-logging>=1.10.0',
    'redis>=3.0.1',
]

setuptools.setup(
    name="mms-pip",
    version="0.5.9",
    author="Josef Goppold",
    author_email="goppold@mediamarktsaturn.com",
    description="A custom MMS/GDWH module for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://source.cloud.google.com/v135-5683-alice-ksk-explore/mms-pip",
    packages=setuptools.find_packages(),
    install_requires=required_packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
