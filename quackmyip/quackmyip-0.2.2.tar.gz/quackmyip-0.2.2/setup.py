from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='quackmyip',
    version='0.2.2',
    description='Updates your IP address for your Duck DNS domain',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tuxedoar/quackmyip',
    author='tuxedoar',
    author_email='tuxedoar@gmail.com',
    packages=['quackmyip'],
    entry_points={
        "console_scripts": [
        "quackmyip = quackmyip.quackmyip:main",
        ],
    },
    install_requires=[
    'urllib3',
    'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        ],
)
