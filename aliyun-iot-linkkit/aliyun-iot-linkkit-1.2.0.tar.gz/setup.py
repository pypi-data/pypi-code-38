import setuptools

with open("README.md", mode='r', encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="aliyun-iot-linkkit",
    version="1.2.0",
    author="Aliyun IoT Linkkit Python SDK",
    author_email="",
    description="Aliyun IoT Linkkit SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=['paho-mqtt', 'hyper', 'crcmod'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
