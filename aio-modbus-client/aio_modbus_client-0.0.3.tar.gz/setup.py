import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aio_modbus_client",
    version="0.0.3",
    author="Mikhail Razgovorov",
    author_email="1338833@gmail.com",
    description="Easy work with modbus device. You do not need to know the protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/businka/aio_modbus_client",
    packages=['aio_modbus_client', ],
    package_data={
        '': ['*.md', '*.json'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO"
    ],
    python_requires='>=3.5.3',
)
