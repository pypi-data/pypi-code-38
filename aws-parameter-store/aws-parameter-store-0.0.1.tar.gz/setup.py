import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["boto3"]

setuptools.setup(
    name="aws-parameter-store",
    version="0.0.1",
    license='apache-2.0',
    description="AWS SSM parameter store client that constructs nested dictionary out of hierarchical path",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Amit Zigelman',                   # Type in your name
    author_email = 'amit.zigelman@vonage.com',      # Type in your E-Mail
    url="https://github.com/Vonage/aws-parameter-store-py",
    packages=setuptools.find_packages(),
    keywords = ['AWS', 'SSM', 'PARAMETER', 'PARAMETER STORE'],
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=install_requires,
)
