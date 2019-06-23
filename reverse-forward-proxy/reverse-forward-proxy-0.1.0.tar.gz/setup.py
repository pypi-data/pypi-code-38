from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="reverse-forward-proxy",
    version="0.1.0",

    author="Chris Hunt",
    author_email="chrahunt@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    description="Reverse proxy for forward proxy",
    entry_points={
        'console_scripts': [
            'reverse-forward-proxy=reverse_forward_proxy.cli:main',
        ],
    },
    extras_require={
        'dev': [
            'aiohttp~=3.5.4',
            'cryptography~=2.7',
            'proxy.py==0.3',
            'pytest~=4.6.3',
            'pytest-aiohttp~=0.3.0',
            'pytest-asyncio~=0.10.0',
            'pytest-asyncio~=0.10.0',
            'requests-async==0.6.2',
        ],
    },
    install_requires=[
        'requests~=2.22.0',
        'yarl==1.3.0',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/chrahunt/reverse-forward-proxy",
)
