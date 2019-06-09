import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyode",
    version="1.0.2",
    author="Ery4z",
    author_email="prog.ery4z@gmail.com",
    description="Easy package to graph ODE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ery4z/easyode",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)