import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "hemApp",
    author = "Ricky Moorhouse",
    author_email = "hem@rickymoorhouse.uk",
    description = ("HTTP Endpoint Monitor - keeping the loose ends tied up"),
    setup_requires = ['setuptools_scm', 'pytest', 'pytest-cov>=2.4.0', 'requests-mock'],
    use_scm_version=True,
    install_requires = ['PyYaml', 'pike', 'click', 'requests', 'dnspython', 'pyjwt'],
    license = "MIT",
    keywords = "monitor, http",
    url = "https://rickymoorhouse.uk/blog/2018/introducing-hem/",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    test_suite = 'nose.collector',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'hem=hemApp.cli:main',
        ],
    },    
)
