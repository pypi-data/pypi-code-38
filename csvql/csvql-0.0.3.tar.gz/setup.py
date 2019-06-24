import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csvql",
    version="0.0.3",
    author="Edgar Nova",
    author_email="ragnarok540@gmail.com",
    description="csvql command line tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="csv, sql, sqlite, csvql, query",
    url="https://github.com/Ragnarok540/csvql",
    py_modules=['csvql'],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'csvql = csvql:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
