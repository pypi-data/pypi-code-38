import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DocuScan",
    version="0.0.1.3",
    author="Alex Scotland",
    author_email="rocketleaguemarket@gmail.com",
    description="A light-weight package that can open document files (docx, doc, pdf)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mutster/DocuScan-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
