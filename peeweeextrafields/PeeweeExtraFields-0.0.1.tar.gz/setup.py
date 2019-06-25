import setuptools

with open('README.md', "r") as readme:
    long_description = readme.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name="PeeweeExtraFields",
    version="0.0.1",
    author="Sergey Parshin",
    author_email="parshinsp@gmail.com",
    description="Collection of Extra Fields for peewee ORM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YADRO-KNS/PeeweeExtraFields",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
