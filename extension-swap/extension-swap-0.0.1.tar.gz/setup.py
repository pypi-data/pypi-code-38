import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="extension-swap",
    version="0.0.1",
    author="Andy Klier",
    author_email="andyklier@gmail.com",
    description="change file extension to nope.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rednap/extension-swap",
    packages = ['nope'],
    entry_points = {
        'console_scripts': ['nope=nope.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
