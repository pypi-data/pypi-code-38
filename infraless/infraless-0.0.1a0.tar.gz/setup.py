from setuptools import setup, find_packages

with open('README.md', 'r') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

with open('requirements.txt') as reqs:
    requirements = reqs.read()

setup(
    name='infraless',
    version='0.0.1-alpha',
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
    install_requires=[
        requirements,
    ],
    entry_points="""
        [console_scripts]
        infraless = infraless.cli_router:main
    """,
)
