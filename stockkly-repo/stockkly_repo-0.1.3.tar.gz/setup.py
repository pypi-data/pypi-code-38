import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stockkly_repo",
    version="0.1.3",
    author="Jamie Wooltorton",
    author_email="james_wooltorton@hotmail.com",
    description="The Stockkly repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/squeakycheese75/stockkly_repo",
    # packages=setuptools.find_packages(),
    packages=['stockkly_repo'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pymongo',
    ],
    license='MIT',
    zip_safe=False
)
