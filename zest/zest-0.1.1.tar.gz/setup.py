import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='zest',  
    version='0.1.1',
    author="Jeremy Zolnai-Lucas",
    author_email="jezza672@gmail.com",
    description="A testing utility package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jezza672/zest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)