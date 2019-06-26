import setuptools

with open("README.md", 'r') as f:
    long_des = f.read()

setuptools.setup(
    name='py-filestore',
    author="Rhys Salkind",
    version='1.0.0',
    description="A python package that implements a static dictionary as a file system.",
    long_description=long_des,
    long_description_content_type="text/markdown",
    url="https://github.com/Caddox/pyfilestore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
