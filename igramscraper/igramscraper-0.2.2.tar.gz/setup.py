import setuptools
from pathlib import Path

setuptools.setup(
    name="igramscraper",
    version="0.2.2",
    description=('scrapes medias, likes, followers, tags and all metadata'),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="MIT",
    maintainer="realsirjoe",
    author='realsirjoe',
    url='https://github.com/realsirjoe/instagram-scraper'
)