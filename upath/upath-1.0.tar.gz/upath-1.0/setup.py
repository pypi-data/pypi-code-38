from setuptools import Extension, setup, find_packages

extension = Extension("upath", ["upath/upath.c", ], extra_compile_args=["-O3"])

setup(
    name="upath",
    version="1.0",
    author='Georgian-Andrei Oprișor',
    author_email='gaoprisor@gmail.com',
    description="""
    C extension to fetch an item from a nested structure made out of dictionaries and/or lists. 
    Can reduce the time spent retrieving items from nested structures resulted after de-serializing JSON content 
    or other nested structures.
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    url="https://github.com/aoprisor/upath",
    license="MIT",
    ext_modules=[extension],
    packages=find_packages(),
    test_suite="tests",
)
