
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csgo-personal-data-collector",
    version="1.0.0",
    author="vaibharn",
    author_email="vaibhav.vaibhavsharan.sharan@gmail.com",
    description="CSGO Competivite Matchmaking Data Collector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vaibharn/AstralisIN-Discord-Bot",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
)