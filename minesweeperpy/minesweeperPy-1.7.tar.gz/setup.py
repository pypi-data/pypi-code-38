from setuptools import setup

with open("READMEPyPi.txt", "r") as README_file:
    long_description = README_file.read()

setup(
    name='minesweeperPy',
    version='1.7',
    description='A Python 3 minesweeper generator module',
    license="MIT",
    long_description=long_description,
    author='stshrewsburyDev',
    author_email='',
    url="https://github.com/stshrewsburyDev/minesweeperPy",
    packages=["minesweeperPy"],
    install_requires=[]
)
