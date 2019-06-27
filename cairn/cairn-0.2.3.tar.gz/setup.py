from setuptools import setup, find_packages

setup(
    name='cairn',
    version='0.2.3',
    description='Tools and utilities for managing project versions',
    url='https://github.com/ejfitzgerald/cairn/',
    author='Ed FitzGerald',
    author_email='edward.fitzgerald@fetch.ai',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=[],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage','pytest', 'tox'],
    },
    entry_points={
        'console_scripts': [
            'cairn=cairn.cli:main',
        ],
    },
)
