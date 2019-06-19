import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emarsysauthenticator",
    version="0.0.1",
    author="Philipp Jaeckle",
    author_email="p.a.jaeckle@gmail.com",
    description="Python helper to easily create X-WSSE header for Authentication with Emarsys RESTful API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datapip/emarsysauthenticator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
