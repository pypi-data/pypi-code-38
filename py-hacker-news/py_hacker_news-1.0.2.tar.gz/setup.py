from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE/ "README.md").read_text()


setup(
    name='py_hacker_news',
    version="1.0.2",
    description="Command Line tool for browsing HackerNews articles",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/saivarshith2000/hacker_news_cli",
    author="saivarshith2000",
    author_email="hosvarshith@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["hnews"],
    include_package_data=True,
    install_requires=["beautifulsoup4", "requests"],
    entry_points={
        "console_scripts":[
            "hnews=hnews.__main__:main"
        ]
    }
),