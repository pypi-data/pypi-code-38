import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tweetlib",
    version="0.2.0",
    author="Wyatt Ferguson",
    author_email="wyattf@gmail.com",
    description="A python twitter scraper with no-api keys required.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wyattferguson/tweetlib",
    packages=['tweetlib'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)