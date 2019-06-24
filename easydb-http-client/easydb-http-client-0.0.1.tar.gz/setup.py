import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easydb-http-client",
    version="0.0.1",
    author="Daniel Fąderski",
    author_email="daniel.faderski@gmail.com",
    description="Http client for Easydb database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prototype-project/easydb-client",
    packages=['easydb'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'aiohttp==3.5.4',
        'async-timeout==3.0.1',
        'attrs==18.2.0',
        'chardet==3.0.4',
        'idna==2.7',
        'multidict==4.4.2',
        'yarl==1.2.6'
    ],
    test_suite='tests.runner'
)
