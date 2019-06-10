import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-test-bed-adapter",
    version="0.0.6",
    author="Hugo J. Bello",
    author_email="hjbello.wk@gmail.com",
    description="This is the test-bed adapter for Python: it allows you to easily connect Python services to the Apache Kafka test-bed via Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DRIVER-EU/python-test-bed-adapter",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)