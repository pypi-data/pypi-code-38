import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gud",
    version="1.0.10",
    author="James Whiteman",
    author_email="james.whiteman@gmail.com",
    description="branch of greengo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/genunity/gud.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'fire',
        'boto3',
        'botocore',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': ['gud=gud.gud:main'],
    },
    license='MIT'
)
