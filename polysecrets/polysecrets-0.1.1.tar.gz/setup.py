import setuptools
from polysecrets.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polysecrets",
    version=__version__,
    author="AbleInc - Jaylen Douglas",
    author_email="douglas.jaylen@gmail.com",
    description="A completely randomized order of secrets, with security in mind.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ableinc/polysecrets",
    keywords=['security', 'polysecrets', 'secrets', 'randomized', 'ableinc', 'cryptography', 'jwt', 'signing',
              'encryption', 'server security', 'application security'],
    packages=['polysecrets'],
    entry_points='''
        [console_scripts]
        polysecrets=polysecrets.cli:cli
    ''',
    install_requires=[
          'Click>=7.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)