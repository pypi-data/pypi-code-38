from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="bn_stemmer",
    version="1.0.0",
    description="A Python package to stem bengali words",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ashwoolford/stemmer",
    author="Ashraf H.",
    author_email="asrafhossain197@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["stemmer"],
    include_package_data=True,
)