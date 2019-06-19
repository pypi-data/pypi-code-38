import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="psd2html",
    version="0.1.5",
    description="Convert PSD file to HTML",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kimngei/psd2html",
    author="Andrew Ngei",
    author_email="andrew@kimngei.pro",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=[
        "psd2html",
        "psd2html.converter",
        "psd2html.builder"
    ],
    include_package_data=True,
    install_requires=[
        "psd-tools",
        "lxml",
        "beautifulsoup4",
        "numpy",
        "scipy",
    ],
    entry_points={
        "console_scripts": [
            "psd2html=psd2html.__main__:main",
        ]
    },
)