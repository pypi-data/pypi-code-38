from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
        print(README.replace("\r", ""))
    return README


setup(
    name="list-slice",
    version="1.0.0",
    description="This library has a function to split the data list into several small sections",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yusriltakeuchi/list-slicer",
    author="Yusril Rapsanjani",
    author_email="yuranicorp@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["listslicer"],
    include_package_data=True,
)