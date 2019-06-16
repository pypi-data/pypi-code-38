from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="TF-Binary-Classification",
    version="1.0.1",
    description="A Python package to get train and test a model for binary classification.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/santos97/TF-Binary-Classification",
    author = "Santosh Shet",
    author_email="santo.shet@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["TF_Binary_Classification"],
    include_package_data=True,
    install_requires=["tqdm", "tensorflow", "mathplotlib", "numpy", "cv2"],
    entry_points={
        "console_scripts": [
            "train=TF_Binary_Classification.train:main",
            "test=TF_Binary_Classification.test:main",
        ]
    },
)