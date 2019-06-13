import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rgn",
    version="0.1.2",
    py_modules=['Rank_Gaussian_Normalization'],
    author="Roger Zhang & Michael Jahrer",
    author_email="shenchaozhang@gmail.com",
    description="Rank Gaussian Normalization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RogerZhangsc/Porto-Seguros-Safe-Driver-Prediction",
    #packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
