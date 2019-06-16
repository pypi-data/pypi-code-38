import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="kaggle_dataset_creator",
    version="0.0.1",
    author="Rishikesh Agrawani",
    author_email="rishikesh0014051992@gmail.com",
    description="A Python package to generate csv/json from command line. It allows you to create CSV/JSON files by asking you to manually enter data for each cells row by row in Terminal (Windows CMD / Bash).",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hygull/kaggle_dataset_creator.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['CSV', 'JSON', 'kaggle', 'dataset', 'Python 3', 'Windows', 'Linux', 'MAC', 'Command line'],
    python_requires='>=3',
    install_requires=['pandas >= 0.23.4', 'colorama >= 0.4.1', 'numpy >= 1.15.4'],
    zip_safe=False
)