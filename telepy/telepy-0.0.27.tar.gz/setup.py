import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="telepy",
    version="0.0.27",
    author="eliko",
    author_email="eliko2411@hi2.in",
    description="Telegram bot library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/2411eliko/tele",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],    
    packages=setuptools.find_packages(),
    install_requires = ["requests"]
)

