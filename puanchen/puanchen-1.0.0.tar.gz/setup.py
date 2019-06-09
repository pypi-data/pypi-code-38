from setuptools import setup, find_packages
import puanchen

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=puanchen.__name__,
    version=puanchen.__version__,
    description="a Python implementation of message queue based on pika",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perfeelab/puanchen",
    author=puanchen.__author__,
    author_email=puanchen.__author_email__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pika>=1.0.1"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)