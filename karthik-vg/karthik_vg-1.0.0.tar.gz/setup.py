from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="karthik_vg",
    version="1.0.0",
    description="A Python package to get weather reports for any location.",
    url="",
    author="karthik_vg",
    author_email="karthikvg1998@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["karthik_vg"],
    include_package_data=True,
    #install_requires=["requests"],
)