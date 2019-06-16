import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-queryset-gallery",
    version="1.0.3",
    author="Eugene Mozge",
    author_email="eumozge@gmail.com",
    description="Queryset gallery is an interface for creating a gallery that provides pagination and filtering via lookups. It can be useful for getting objects via API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eumozge/django-queryset-gallery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
