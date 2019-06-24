from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="lsg",
    version="0.1.0",
    author="Justine T Kizhakkinedath",
    author_email="justine@kizhak.com",
    description="A better alias for `ls | grep`",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/justinethomas/lsg",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="command-line tool search files and folders",
    entry_points={
        "console_scripts": ["lsg = lsg.main:main"],
    },
    project_urls={
        "Bug Reports": "https://gitlab.com/justinekizhak/lsg/issues",
        "Say Thanks!": "http://saythanks.io/to/justinekizhak",
        "Source": "https://gitlab.com/justinekizhak/lsg",
    },
)
