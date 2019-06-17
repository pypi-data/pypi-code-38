import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webguitest-scubbx",
    version="0.0.14",
    author="Markus Mayr",
    author_email="markusmayr@gmx.net",
    description="A web user interface test module combining Selenium and pyautogui into one interface ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scubbx/webguitest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
