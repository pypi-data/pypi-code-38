import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clericus",
    version="0.0.3a4",
    author="Joseph L Buell V",
    author_email="jlrbuellv@gmail.com",
    description=
    "An async webserver focused on being predictable and self documenting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrincredibuell/clericus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
        "aiohttp>=3.5.4",
        "pyjwt>=1.7.1",
        "motor>=2.0.0",
        "python-dateutil>=2.8.0",
        "bcrypt>=3.1.6",
        "dnspython>=1.16.0",
        "faker>=1.0.7",
    ],
)