from setuptools import setup, find_packages

setup(
    name='porkpepper',
    version='0.1.0',
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
        'base58',
        'aiohttp',
        'typing',
        'pytest',
        'aioredis',
        'pytest-asyncio',
    ],
    tests_require=[
        'pytest',
    ],
)
