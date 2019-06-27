import setuptools

setuptools.setup(
    name="SquirrelDB",
    version='0.2.0',
    author="Vigneash Sundararajan",
    author_email = "vigneashsundar@live.com",
    description="Typesafe In-Memory datastore written in Python.",
    packages=setuptools.find_packages(),
    license = 'GPL',
    long_description=open('README.MD').read(),
    url = "https://github.com/vikene/squirreldb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
