import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cntkx",
    version="0.1.10",
    author="delzac",
    author_email="delzac.jh@gmail.com",
    description="Extension library of Microsoft Cognitive Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/delzac/cntkx",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
