import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bisnode",
    version="0.0.1",
    author="Bismuth Foundation",
    author_email="admin@bismuth.cz",
    description="Bismuth Node",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bismuthfoundation/Bismuth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=['PySocks','pycryptodomex','pillow','pyqrcode','matplotlib','ed25519','base58','coincurve'],
)