from setuptools import setup, find_packages

import quotly

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='quotly',
    version=quotly.__version__,
    packages=find_packages(exclude="web"),
    author='Schrotty',
    author_email='rubenmaurer@live.de',
    description='A quoting bot for the "Discord Hack Week"',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license='MIT',
    keywords='discord discord-bot',
    url='https://github.com/Schrotty/quotly',
    install_requires=[
        'python-dotenv',
        'discord.py'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
