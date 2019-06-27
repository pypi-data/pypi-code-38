import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pyconfluent",
    version="0.0.6",
    author="Peter Newell",
    author_email="peter.newell@covetrus.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitbub.com/newellp2019/pyconfluent",
    packages=setuptools.find_packages(),
    install_requires=["requests", "confluent-kafka[avro]", "avro-python3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
