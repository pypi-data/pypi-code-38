from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="adansonia",
    version="0.0.6",
    author="mlabarrere",
    author_email="mlabarrere@baobab.bz",
    description="Utils package for common operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baobab-group/Adansonia",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent", "Natural Language :: English"
    ],
    install_requires=[
        'numpy', 'pandas', 'google-cloud-bigquery', 'google-api-python-client',
        'google-auth-httplib2', 'google-auth-oauthlib', 'pyarrow'
    ],
)
