import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-random-image-from-folder",
    version="0.0.2",
    author="Ilya_Bat9",
    author_email="nasirov@olympus.ru",
    description="Django Random Image From Folder is a simple app to load a random image from a specified directory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IlyaBat9/django-random-image-from-folder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
    ],
)