from setuptools import setup

def readme():
    with open("readme.md") as f:
        r = f.read()
    return r


setup(
    name = "badvillain-python-package",
    version = "1.0.0",
    description = "Hello idk what to say",
    long_description = readme(),
    long_description_content_type = "text/markdown",
    url = "https://www.thevillainer.tk/",
    author = "Badvillain",
    author_email = "idk@gmail.com",
    license = "MIT",
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages = ["badvillain_greeting"],
    setup_requires = ['wheel']
)