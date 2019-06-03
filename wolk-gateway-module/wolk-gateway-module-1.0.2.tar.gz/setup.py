from os import path

import setuptools

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="wolk-gateway-module",
    version="1.0.2",
    install_requires=["paho_mqtt==1.4.0"],
    include_package_data=True,
    license="Apache License 2.0",
    author="WolkAbout",
    author_email="info@wolkabout.com",
    description=(
        "SDK for gateway communication modules "
        "that connect to WolkAbout IoT Platform"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["IoT", "WolkAbout", "Internet of Things"],
    url="https://github.com/Wolkabout/WolkGatewayModule-SDK-Python",
    packages=setuptools.find_packages(exclude=("test",)),
    test_suite="unittest",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Software Development :: Embedded Systems",
    ],
)
