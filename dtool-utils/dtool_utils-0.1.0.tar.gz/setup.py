from setuptools import setup

url = ""
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool_utils",
    packages=["dtool_utils"],
    version=version,
    description="Dtool utility functions and classes",
    long_description=readme,
    include_package_data=True,
    author="Matthew Hartley",
    author_email="matthew.hartley@jic.ac.uk",
    url=url,
    install_requires=[
        "dtoolcore>=3.0.0",
        "ruamel.yaml",
    ],
    #download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
