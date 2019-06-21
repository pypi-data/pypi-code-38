import setuptools

with open("./iotery_python_server_sdk/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iotery-python-server-sdk",
    version="0.0.4",
    author="bjyurkovich",
    author_email="bj.yurkovich@technicity.io",
    description="iotery.io python server SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bjyurkovich/iotery-python-server-sdk",
    # packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[('api', ['iotery_python_server_sdk/api.json'])],
    license='MIT',
    packages=['iotery_python_server_sdk'],
    install_requires=["requests"],
    include_package_data=True
)
