from os import path

from setuptools import setup, find_packages

version = "0.1.12"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="perestroika",
    packages=find_packages(),
    version=version,
    description="Rest lib",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Ruslan Roskoshnyj",
    author_email="i.am.yarger@gmail.com",
    url="https://github.com/newmediatech/perestroika",
    download_url="https://github.com/newmediatech/perestroika/archive/{}.tar.gz".format(version),
    keywords=["REST"],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django :: 2.2',
    ],
    python_requires=">3.6.0",
    platforms=["OS Independent"],
    license="LICENSE.txt",
    install_requires=[
        "attrs (==19.1.0)",
    ],
    extras_require={
        "tests": [
            "pytest (==3.6.0)",
            "coverage (==4.5)",
            "pytest-cov (==2.5.1)",
            "django (==2.2)",
            "pytest-django (==3.2.0)",
        ],
        "docs": []
    }
)
