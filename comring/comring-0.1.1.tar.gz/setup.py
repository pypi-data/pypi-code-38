from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="comring",
    version="0.1.1",
    author="Agustianes Umbara Suwardi",
    author_email="anezch@gmail.com",
    description="Comring, the PTI ERP companion tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ausuwardi/comring",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'flask',
        'cheroot',
        'cryptography',
        'requests',
        'python-dotenv',
        'PyYAML',
        'pika',
        'xlrd',
        'prettytable',
        'cachetools',
        'wsgi-request-logger',
        'coloredlogs',
    ],
)
