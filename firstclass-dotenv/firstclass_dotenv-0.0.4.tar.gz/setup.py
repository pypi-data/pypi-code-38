import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="firstclass_dotenv",
    version="0.0.4",
    author="Hajime Kurita",
    author_email="support@1stclass.co.jp",
    description="Read value of .env(dotenv) into ENV values",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hikarine3/firstclass_dotenv",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
