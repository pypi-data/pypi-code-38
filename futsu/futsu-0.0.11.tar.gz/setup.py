import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="futsu",
    version="0.0.11",
    author="Luzi Leung",
    author_email="luzi82@gmail.com",
    description="Very reusable python code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luzi82/py.futsu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    test_suite='nose.collector',
    install_requires=['lazy-import'],
    tests_require=['nose'],
    python_requires='>=3',
)
