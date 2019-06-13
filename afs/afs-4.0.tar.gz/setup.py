import setuptools  

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="afs",
    version="4.0",
    author="SYSTEM CORP.",
    author_email="contact@systemcorp.ai",
    description="Agent for Neural Network training supervision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/systemcorp-ai/TAFNN/archive/2.3.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
)
