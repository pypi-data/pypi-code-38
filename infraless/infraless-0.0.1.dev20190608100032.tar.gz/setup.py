from setuptools import setup, find_packages
from infraless.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='infraless',
    version=VERSION,
    description='Run your code at scale without worrying about the cloud',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Pulkit Kumar',
    author_email='ispulkitkr@gmail.com',
    url='https://github.com/ispulkit',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'infraless': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        infraless = infraless.cli_router:main
    """,
)
