from setuptools import setup, find_packages

readme = open('README.md').read().strip()

setup(
    name='testaton',
    version='0.1.8',
    license='MIT',
    author='Michael Farrugia',
    author_email='mike.farrugia@gmail.com',
    url='https://github.com/mikelupu/testaton',
    description='A command line tool to allow the testing of datasets',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        # put packages here
        'six',
        'findspark',
        'pandas',
        'sqlalchemy',
        'dtest-framework',
        'pyhamcrest'
    ],
    test_suite='tests',
    entry_points={'console_scripts': ['testaton = testaton.cli:main']}
)
