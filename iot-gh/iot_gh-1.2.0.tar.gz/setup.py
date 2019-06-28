import setuptools
from pkg_resources import Requirement, resource_filename

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iot_gh",
    version="1.2.0",
    author="Keith E. Kelly",
    author_email="kkelly@k2controls.net",
    description="IoT Greenhouse service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/k2controls/iot_gh.git",
    packages=setuptools.find_packages(),
    package_data = {"": ["*.conf", "*.csv"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Education",
        "Development Status :: 3 - Alpha"
    ]
  
)
