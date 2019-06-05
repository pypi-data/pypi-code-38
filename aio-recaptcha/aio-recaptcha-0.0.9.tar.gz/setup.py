import setuptools
import os

with open("README.md", encoding="utf-8") as readmef:
    readme = readmef.read()

setuptools.setup(
    name="aio-recaptcha",
    version="0.0.9",
    author="Omar Ryhan",
    author_email="omarryhan@gmail.com",
    license="MIT",
    description="Recaptcha v2 and v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires="aiohttp",
    tests_require=["pytest", "pytest-asyncio", "sanic"],
    url="https://github.com/omarryhan/aio-recaptcha",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
