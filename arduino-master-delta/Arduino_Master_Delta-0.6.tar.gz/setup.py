import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Arduino_Master_Delta",
    version="0.6",
    author="Sayad Pervez",
    author_email="pervez2504@gmail.com",
    description="Data Science enabled Data extraction and control library for Arduino with accurate Data Visualizations !.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SayadPervez/Arduino_Master_Delta",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
