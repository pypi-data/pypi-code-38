import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="purple_bio",
    version="0.4.2.4",
    author="Johanna Lechner, Pauline Hiort and Felix Hartkopf",
    author_email="lechnerJ@rki.de, hartkopff@rki.de",
    description="Picking Unique Relevant Peptides for viraL Experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/HartkopfF/Purple",
    packages=setuptools.find_packages(),
    install_requires=[
          'tqdm',
          'biopython',
          'pyyaml'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
	    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)

