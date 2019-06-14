import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beetrack_uploader-nkipreos",
    version="0.0.1",
    author="Nicolas Kipreos",
    author_email="nicolas.kipreos@beetrack.com",
    description="A simple and small wrapper for uploading files to Beetrack using Python scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nkipreos/BeetackUploader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
