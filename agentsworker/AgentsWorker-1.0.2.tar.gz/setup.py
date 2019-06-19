import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AgentsWorker",
    version="1.0.2",
    author="Enoi Barrera Guzman",
    author_email="zafiro3000x@gmail.com",
    description="Libreria para crear agentes que responden a eventos desde kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['kafka==1.3.5', 'Logbook==1.4.3']
)