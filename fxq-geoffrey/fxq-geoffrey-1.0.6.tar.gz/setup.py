import pathlib

from setuptools import setup

setup(
    name='fxq-geoffrey',
    version='1.0.6',
    packages=['fxq.geoffrey'],
    url='https://bitbucket.org/fxquants/geoffrey',
    license='MIT',
    author='Jonathan Turnock',
    author_email='Jonathan.Turnock@fxquants.net',
    description='The Provisioning Assistant for Devops, configure snippets as YML and call them from the geoffrey CLI',
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=['Click', 'fxq-core', 'pyfiglet', 'PyInquirer', 'PyYAML', 'appdirs'],
    entry_points={
        'console_scripts': ['geoffrey=geoffrey.cli:main'],
    }
)
