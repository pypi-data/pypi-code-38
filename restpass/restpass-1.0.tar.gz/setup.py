import setuptools
from restpass import NAME, VERSION


with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()

description = "A terminal based graphical generator for restorable passwords"
assert description == LONG_DESCRIPTION.split("\n")[1]

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="BananaLoaf",
    author_email="bananaloaf@protonmail.com",
    keywords=["string", "str", "generator", "password", "passphrase", "hash", "restore"],
    license="MIT",
    description=description,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=f"https://github.com/BananaLoaf/{NAME}",
    download_url=f"https://github.com/BananaLoaf/{NAME}/archive/v{VERSION}.tar.gz",
    install_requires=["seedrandom", "npyscreen", "pyperclip"],
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": [f"{NAME} = {NAME}.app:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
