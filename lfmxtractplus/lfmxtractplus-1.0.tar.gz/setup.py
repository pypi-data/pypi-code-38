from setuptools import setup

setup(
    name='lfmxtractplus',
    version='1.0',
    author='Madhan Balaji',
    author_email='madhanbalaji2000@gmail.com',
    packages=['lfmxtractplus'],
    license='LICENSE',
    description='Utility to extract last.fm scrobbles as a Pandas dataframe and enhance it with spotify audio features',
    install_requires=[
        "PyYAML >= 5.1.1",
        "numpy >= 1.14.0",
        "pandas >= 0.22.0",
        "requests >= 2.22.0",
        "spotipy >= 2.4.4",
        "tqdm >= 4.31.1",

    ],
)
