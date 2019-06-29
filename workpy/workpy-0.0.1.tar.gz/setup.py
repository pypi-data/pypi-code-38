import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="workpy",
    version="0.0.1",
    author="cofear",
    author_email="cofear@163.com",
    description="working with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cofear/workpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)