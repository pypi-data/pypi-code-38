from setuptools import setup

NAME = 'aninja'
DESCRIPTION = 'Help your spiders deal with anti-crawling mechanism.'
URL = 'https://github.com/wooddance/aNinja'
EMAIL = 'zireael.me@gmail.com'
AUTHOR = 'wooddance'
VERSION = '0.0.1'

packages = ['aninja']
requires = [
    'requests-html',
    'dateparser',
    'aiohttp',
    'pillow',
]
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires='>=3.6.0',
    packages=packages,
    install_requires=requires,
)
