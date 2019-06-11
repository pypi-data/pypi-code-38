import setuptools
from pathlib import Path

setuptools.setup(
    name="igramscraper",
    version="0.2.3",
    description=('scrapes medias, likes, followers, tags and all metadata'),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="MIT",
    maintainer="realsirjoe",
    author='realsirjoe',
    url='https://github.com/realsirjoe/instagram-scraper',
    install_requires=[
        'requests==2.21.0',
        'bs4==0.0.1',
        'python-slugify==3.0.2'
    ],
)