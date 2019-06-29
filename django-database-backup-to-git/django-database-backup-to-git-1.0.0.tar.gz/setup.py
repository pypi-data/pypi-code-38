import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-database-backup-to-git",
    version="1.0.0",
    author="Eerik Sven Puudist",
    author_email="eerik@herbfoods.eu",
    description="Django specific database backup system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eeriksp/django-database-backup-to-git",
    packages=setuptools.find_packages(),
    install_requires=[
        'django',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
