import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nbtimebar",
    version="0.2.0",
    author="Maciej Rapacz",
    author_email="parallel.bars@gmail.com",
    description="Widget based progress bar for Jupyter (IPython Notebook)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrapacz/log-progress",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
