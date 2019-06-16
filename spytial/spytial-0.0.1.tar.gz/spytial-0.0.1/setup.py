import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spytial",
    version="0.0.1",
    author="Jiabin Liu",
    author_email="ljbliujiabin@gmail.com",
    description="A package to analyze geographical statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jiabin-liu/spytial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)