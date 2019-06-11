import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyCybex",
    version="1.1.3",
    author="yoyo.zhou",
    author_email="yoyo.zhou@cybex.io",
    description="Use this lib to visit public data on cybex decentralized exchange like account,\
 marketing, asset and balance.Also,\
 it can be used to manage a wallet for user and send transactions to cybex chain",
    install_requires=[
        'bitshares==0.1.13',
        'graphenelib==0.6.1',
        'requests>=2.19.0',
        'coincurve==11.0.0'
    ],

    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CybexDEX/cybex-node-doc",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

