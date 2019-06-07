import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ez_elb",
    version="0.5.1",
    author="Dan Boitnott",
    author_email="boitnott@sigcorp.com",
    description="Easily define complex ELB CloudFormation templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dboitnot/ez_elb",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'troposphere>=2.3.1'
    ]
)
