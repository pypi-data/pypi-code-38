from setuptools import setup
from os import path

cd = path.abspath(path.dirname(__file__))
with open(path.join(cd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="jshort",
    version="1.1.2",
    py_modules=["j"],
    description="Json shorthand for python",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Eric Régnier",
    author_email="utopman@gmail.com",
    license="MIT",
    install_requires=["pygments", "jsonpath-ng"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: Jython",
        "Intended Audience :: Developers",
    ],
    keywords=["utility", "json", "tool"],
    url="http://github.com/eregnier/j",
)
