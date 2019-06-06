import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pitch",
    version="0.0.6",
    author='''Sunil Karamchandani,
                Parth M,
                Bhargav D,
                Atulya K,
                Sanjeet K,
                Viren B''',
    description="To find pitch of an audio file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ParthMehta15/Pitch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
