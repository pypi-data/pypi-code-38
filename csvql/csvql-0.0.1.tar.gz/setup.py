import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csvql",
    version="0.0.1",
    author="Edgar Nova",
    author_email="ragnarok540@gmail.com",
    description="CSV-SQL Command Line Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ragnarok540/csv-sql",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
