import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AgentsWorker",
    version="1.0.6",
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
    install_requires=['kafka-python==1.4.6', 'Logbook==1.4.3']
)