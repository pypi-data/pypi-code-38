from setuptools import setup, find_packages

setup(
    name="hrisapi",
    version="0.0.2",
    packages=["hrisapi"],
    url="https://github.com/deep-compute/hrisapi",
    install_requires=[
        "basescript==0.2.8",
        "graphene==2.1.3",
        "tornadoql>=0.1.7",
        "requests==2.21.0",
        "deeputil==0.2.5",
        "timezonefinder==4.0.2",
        "geopy==1.19.0",
        "PyMemoize==1.0.3",
        "redis==3.2.1",
    ],
    author="deep-compute",
    author_email="contact@deepcompute.com",
    description="Human Resource Information Systems API",
    keywords=["hris", "hrisapi", "hrms"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["hrisapi = hrisapi:main"]},
)
