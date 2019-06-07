import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inapp_file_lib-rjanoop",
    version="1.0.1",
    author="RJ Anoop",
    author_email="mail.anooprj@gmail.com",
    description="Library to read and write raw data file and create dictionary based of definition models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rjanoop/inapp_file_lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)