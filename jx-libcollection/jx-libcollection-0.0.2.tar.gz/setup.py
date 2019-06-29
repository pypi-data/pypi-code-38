import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jx-libcollection",
    version="0.0.2",
    author="jiao.xue",
    author_email="jiao.xuejiao@gmail.com",
    description="Jiao's collection libs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caser789/libcollection",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
