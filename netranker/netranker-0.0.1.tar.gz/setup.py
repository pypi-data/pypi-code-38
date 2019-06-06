import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="netranker",
    version="0.0.1",
    author="Daniel Strong",
    author_email="dstrong@glyx.co.uk",
    description="Flask APIs for netranker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ouroboros8/netranker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'flask',
        'flask-restful',
        'PyJWT',
        'pymongo',
    ],
)
