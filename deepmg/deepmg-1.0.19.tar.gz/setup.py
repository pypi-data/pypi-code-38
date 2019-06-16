import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deepmg",
    version="1.0.19",
    author="Thanh-Hai Nguyen",
    author_email="hainguyen579@gmail.com",
    description="A python package to visualize/train/predict data using machine/deep learning algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.integromics.fr/published/deepmg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    license='GPLv3+'
)

