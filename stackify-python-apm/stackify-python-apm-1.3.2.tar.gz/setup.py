import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stackify-python-apm",
    version="1.3.2",
    author="Stackify",
    author_email="support@stackify.com",
    description="This is the official Python module for Stackify Python APM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.stackify.com",
    packages=setuptools.find_packages(),
    zip_safe=True,
    install_requires=["blinker>=1.1"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
)
