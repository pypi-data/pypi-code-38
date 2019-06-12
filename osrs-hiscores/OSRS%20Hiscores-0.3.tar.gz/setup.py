import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='OSRS Hiscores',  
    version='0.3',
    author="Coffee Fueled Deadlines",
    author_email="cookm0803@gmail.com",
    description="An Old School Runescape (OSRS) Hiscore Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Coffee-fueled-deadlines/osrs-hiscores",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)