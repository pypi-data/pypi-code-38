import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywayman",
    version="0.0.3",
    author="Monica Shapiro",
    author_email="monshapiro@gmail.com",
    description="Move Windows lock-screen photos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monshap/pywayman",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
)