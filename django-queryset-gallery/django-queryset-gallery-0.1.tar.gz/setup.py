import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-queryset-gallery",
    version="0.1",
    author="Eugene Mozge",
    author_email="eumozge@gmail.com",
    description="The gallery for queryset that supports interface for filtering",
    long_description_content_type="text/markdown",
    url="https://github.com/eumozge/django-queryset-gallery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
