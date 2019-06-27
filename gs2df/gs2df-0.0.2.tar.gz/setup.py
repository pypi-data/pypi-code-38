import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="gs2df",
    version="0.0.2",
    author="Zhijie Huang",
    author_email="hzj1872@gmail.com",
    url="https://github.com/users/tianco10/projects/1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)