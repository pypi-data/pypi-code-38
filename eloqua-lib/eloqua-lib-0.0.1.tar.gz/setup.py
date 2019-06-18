import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eloqua-lib",
    version="0.0.1",
    author="Josh Norton",
    author_email="joshrnorton75@gmail.com",
    description="Eloqua library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jnorton2/Eloqua",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)