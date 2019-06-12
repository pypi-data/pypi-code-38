import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SplitMerge",
    version="0.0.2.post",
    author="Satyaki De",
    author_email="satyaki.de@gmail.com",
    description="Split & Merge utilities for large csv files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SatyakiDe2019/SplitMerge",
    packages=setuptools.find_packages(),
	install_requires=[
          'markdown','pandas',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)