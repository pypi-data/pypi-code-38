import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jkl_serialization",
    version="0.0.1",
    author="Daan Knoope",
    author_email="daan@knoope.dev",
    description="(De)Serialization of JKL objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daanknoope/jkl-serialization",
    python_requires='>3.6',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)