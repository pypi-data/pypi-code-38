from setuptools import setup, find_packages
from setuptools.command.install import install

setup(
    name="pactly",
    version="0.10",
    description="fastText prototype",
    url="http://pactly.ai",
    author="Alara Dirik",
    author_email="alara@pactly.ai",
    license="MIT",
    packages=["pactly"],
    install_requires=["Keras==2.1.2", "numpy==1.16", "pandas==0.24.1", "dill"],
    zip_safe=False,
)
