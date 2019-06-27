from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pwnlink',
    version='1.1',
    packages=['pwnlink'], 
    install_requires = ["requests"],
    description='A python3 tool for extracting admin passwords from D-link routers without authentication',
    url='https://github.com/Ewpratten/pwnlink',
    author='Evan Pratten',
    author_email='ewpratten@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ),
    entry_points={
        'console_scripts': [
            'pwnlink = pwnlink.__main__:main'
        ]
    })
