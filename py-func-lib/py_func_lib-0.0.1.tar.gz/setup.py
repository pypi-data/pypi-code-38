import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_func_lib",
    version="0.0.1",
    author="Joe Cuffney",
    author_email="josephcuffney@gmail.com",
    description="Functional Library for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jcuffney/py-func-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)