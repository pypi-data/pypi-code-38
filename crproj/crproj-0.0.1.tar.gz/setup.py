import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crproj",
    version="0.0.1",
    author="Bhavay Pahuja",
    author_email="bhavay.pahuja@gmail.com",
    description="A terminal tool to start new projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bpahuja/proj",
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts':['proj=proj.main:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)