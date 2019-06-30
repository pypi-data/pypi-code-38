from setuptools import setup, find_packages

setup(
    name='porkpepper',
    version='0.2.0',
    author='宋伟(songwei)',
    author_email='songwei@songwei.io',
    long_description='',
    url='https://github.com/xdusongwei/porkpepper',
    packages=find_packages(),
    ext_modules=[],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'Jinja2',
        'base58',
        'aiotools',
        'aiohttp',
        'typing',
        'pytest',
        'aioredis',
        'pytest',
        'pytest-asyncio',
        'python-coveralls',
        'pytest-cov',
        'codecov',
    ],
    tests_require=[
        'pytest',
    ],
)
