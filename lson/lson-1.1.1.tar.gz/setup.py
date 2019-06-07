import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lson",
    version="1.1.1",
    author="Alex Broaddus",
    author_email="alexbroaddus1@gmail.com",
    description="Display directory structure in json format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts': ['lson=lson.command_line:main']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)