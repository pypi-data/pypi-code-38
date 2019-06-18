from setuptools import setup, find_packages


with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='sitesize',
    version='0.0.1',
    author='Siddhant Shaw',
    author_email='siddhantshaw97@gmail.com',
    description='Get size of web page',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/mianto/sitesize',
    packages=find_packages(exclude=('tests')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)