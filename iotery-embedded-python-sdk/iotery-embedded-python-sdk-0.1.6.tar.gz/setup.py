import setuptools

with open("./iotery_embedded_python_sdk/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iotery-embedded-python-sdk",
    version="0.1.6",
    author="bjyurkovich",
    author_email="bj.yurkovich@technicity.io",
    description="iotery.io embedded python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bjyurkovich/iotery-embedded-python-sdk",
    # packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[('api', ['iotery_embedded_python_sdk/api.json'])],
    license='MIT',
    packages=['iotery_embedded_python_sdk'],
    install_requires=["requests"],
    include_package_data=True
)
