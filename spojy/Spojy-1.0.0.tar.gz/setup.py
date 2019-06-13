from distutils.core import setup

setup(
    name='Spojy',
    version='1.0.0',
    author='Aniruddha Bhattacharjee',
    author_email='aniruddha97bhatt@gmail.com',
    packages=['spojy', 'spojy.test'],
    scripts=["bin/sample.py"],
    url='http://pypi.python.org/pypi/Spojy/',
    license='LICENSE.txt',
    description='Useful to gather all relevent information about problems and users from the popular problem solving site SPOJ.',
    long_description=open('README.md').read(),
    install_requires=[
        "bs4 >= 4.6.0",
        "asyncio >= 3.4.3",
        "aiohttp >= 3.5.4",
        "requests >= 2.18.4",
    ],
)
