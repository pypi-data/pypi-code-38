from setuptools import find_packages, setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README
 


setup(
    name="bnltk",
    version="0.7.3",
    description="BNLTK(Bangla Natural Language Processing Toolkit) is open-source python package for Bengali Natural Language Processing.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ashwoolford/bnltk",
    author="Ashraf Hossain",
    author_email="asrafhossain197@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["keras", "tensorflow", "numpy", "sklearn", "requests"],
)
