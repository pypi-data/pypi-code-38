import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Rado",
    version="0.0.2",
    author="lit",
    author_email="tt137378245@outlook.com",
    description="The InterFace Test Framework based on PyTest, Request and Allure", # noqa
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheoTT/my_doc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'allure-pytest==2.6.5',
        'Click==7.0',
        'colorama==0.4.1',
        'colorlog==4.0.2',
        'datatest==0.9.6',
        'jsonpath==0.81',
        'paramiko==2.5.0',
        'xlrd==1.2.0',
        'requests==2.22.0',
    ],
    extras_require={
        'Rado': []
    },
    entry_points={
        'console_scripts': 'rado = rado.rado:cli'
    }
)
