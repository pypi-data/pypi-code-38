from distutils.core import setup

setup(
    name="whatbuild",
    version="0.0.2",
    description="Print simple git and system information as JSON",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/inorton/whatbuild",
    packages=["whatbuild"],
    install_requires=['gitpython'],
    platforms=["any"],
    license="License :: OSI Approved :: MIT License"
)
