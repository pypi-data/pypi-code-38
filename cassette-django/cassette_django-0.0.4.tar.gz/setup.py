try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cassette_django',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.0.4',
    author='Joachim Lindqvist',
    author_email='lindqvist.joachim@gmail.com',
    packages=[
        'cassette_django',
    ],
    scripts=[],
    url="https://github.com/cassette-dev/cassette-django",
    install_requires=[
        'requests',
        'Django >= 1.8.0',
        'requests_toolbelt',
    ]
)