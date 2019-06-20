from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='PCPPScraper',
    version='1.3',
    description='A simple scraper for PCPP Lists',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/A1phyte/PCPPScraper',
    author='Bryan Li',
    author_email='bryanyuezhouli@gmail.com',
    license='MIT',
    packages=['PCPPScraper'],
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    zip_safe=False)