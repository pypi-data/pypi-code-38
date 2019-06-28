from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="systime_stackapi",
    version="0.0.17",
    author="Rasmus Larsen",
    author_email="rla@systime.dk",
    description="A python API for accessing Systimes infrastructure services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/systime/systime-stack-python-api",
    packages=['systime_stackapi', 'systime_stackapi.cli', 'systime_stackapi.cli.commands'],
    install_requires=[
        'requests>=2.22.0',
        'dnspython==1.15.0',
        'PyJWT==1.7.1',
        'Click==7.0',
        'fcache==0.4.7'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        stackcli=systime_stackapi.cli.stackcli:cli
    ''',
)
