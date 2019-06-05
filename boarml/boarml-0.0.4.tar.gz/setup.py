import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boarml",
    version="0.0.4",
    author="Dobromir Marinov",
    author_email="mr.d.marinov@gmail.com",
    description="Package for building abstract ML models that can then be compiled using popular ML platforms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DobromirM/BoarML",
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
