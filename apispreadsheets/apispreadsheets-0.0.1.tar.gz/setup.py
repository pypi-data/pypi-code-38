import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apispreadsheets",
    version="0.0.1",
    author="API Spreadsheets Team",
    author_email="info@apispreadsheets.com",
    description="Library for API Spreadsheets Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asharma327/apispreadsheets_python_lib.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests'
    ]
)

# python3 setup.py sdist bdist_wheel
# twine upload dist/*