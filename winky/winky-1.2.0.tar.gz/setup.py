from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='winky',
    version='1.2.0',
    packages=['winky'],
    url='https://bitbucket.org/alborov/winky',
    license='MIT',
    author='Zaur Alborov',
    author_email='alborov.z@gmail.com',
    description='API Test Framework',
    install_requires=['requests==2.21.0', 'lxml==4.3.1', 'pytest==4.6.3', 'allure-pytest==2.6.5'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
