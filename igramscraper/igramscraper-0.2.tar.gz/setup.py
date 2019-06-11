import setuptools
from pathlib import Path

setuptools.setup(
    name="igramscraper",
    version=0.2,
    description=('scrapes medias, likes, followers, tags and all metadata'),
    long_description=('Interacts with Instagrams private API through http requests only, perfect for multithreading, scrapes medias, likes, followers and all metadata. Also can be used to like, unlike, follow, unfollow, comment, uncomment.'),
    packages=setuptools.find_packages(),
    license="MIT",
    maintainer="realsirjoe",
    author='realsirjoe',
    url='https://github.com/realsirjoe/instagram-scraper'
)