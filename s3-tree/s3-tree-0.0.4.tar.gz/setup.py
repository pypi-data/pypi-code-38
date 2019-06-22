import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="s3-tree",
    version="0.0.4",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="list s3 objects in tree-like format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rednap/s3-tree",
    packages = ['s3tree'],
    entry_points = {
        'console_scripts': ['s3-tree=s3tree.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
