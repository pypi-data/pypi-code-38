import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tzhutils",
    version="0.0.1",
    author="tzh",
    author_email="13060820957@163.com",
    description="A small utils for decorator package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/664956016/tzhutils.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    include_package_data = True,
    install_requires = ["progressbar"]  
)