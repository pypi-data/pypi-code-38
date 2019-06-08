import pip

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except:
    with open('README.md', 'r') as readme_file:
        LONG_DESCRIPTION = readme_file.read()

with open('requirements.txt', 'r') as req:
    requirements = req.read()

setup(
    name='infraless',
    version='0.0.04-alpha',
    description='Run your code at scale without worrying about the cloud',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Pulkit Kumar',
    author_email='ispulkitkr@gmail.com',
    url='https://github.com/ispulkit',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={
        'infraless': ['templates/*', 'requirements.txt'],
    },
    include_package_data=True,
    install_requires=[
        requirements,
    ],
    entry_points="""
        [console_scripts]
        infraless = infraless.cli_router:main
    """,
)
