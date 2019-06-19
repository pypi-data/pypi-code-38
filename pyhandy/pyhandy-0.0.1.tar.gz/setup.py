import setuptools

with open("README.md", "r") as f:
    long_descripton = f.read()

setuptools.setup(
        name="pyhandy",
        version="0.0.1",
        author="callmexss",
        author_email="callmexss@126.com",
        description="A collection of tools to make my life easier.",
        long_descripton=long_descripton,
        long_descripton_content_type="text/markdown",
        url="https://github.com/callmexss/pyhandy",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent"
            ]
        )

