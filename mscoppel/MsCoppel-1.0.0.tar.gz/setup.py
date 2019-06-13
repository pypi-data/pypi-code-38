import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MsCoppel",
    version="1.0.0",
    author="Enoi Barrera Guzman",
    author_email="zafiro3000x@gmail.com",
    description="Libreria para microservicios basados en mensajes desde kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['kafka==1.3.5', 'Logbook==1.4.3']
)