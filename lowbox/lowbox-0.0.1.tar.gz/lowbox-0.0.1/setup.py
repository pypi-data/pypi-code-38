import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lowbox",
    version="0.0.1",
    author="Wallace Silva",
    author_email="contato@wallacesilva.com",
    description="A simple alternative in python to busybox and toybox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallacesilva/lowbox",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
