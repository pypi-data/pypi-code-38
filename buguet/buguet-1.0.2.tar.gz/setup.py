import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buguet",
    version="1.0.2",
    author="dr6kl",
    author_email="dr6kl@protonmail.com",
    description="Ethereum debugger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dr6kl/buguet",
    packages=setuptools.find_packages(),
    license = "GPL",
    install_requires=[
        'web3 >=4.7.2, <5',
        'pysha3 >=1.0.2, <2',
        'termcolor >=1.1.0, <2'
    ],
    entry_points={
        'console_scripts': [
            'buguet = buguet.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
)
