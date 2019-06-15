import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-crud-routes",
    version="0.0.2",
    author="Amrendra Kumar",
    author_email="aks23101@gmail.com",
    description="Flask CRUD Router",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kuamrend/flask-crud-routes",
    packages=setuptools.find_packages(),
    install_requires=[
        'inflection'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
