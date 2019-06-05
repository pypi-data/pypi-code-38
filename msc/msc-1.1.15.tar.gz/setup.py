import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="msc",
    version="1.1.15",
    author="Sergio Jimenez",
    author_email="menine77@gmail.com",
    description="libreria para hacer la conexion de microservicios, cambio para los asincronos que se borren los datos cada 3 minutos, llamados asincronos en ves de hilos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=[
    'simplejson==3.16.0',
    'pymongo==3.7.2',
    'kafka==1.3.5',
    'requests==2.20.0',
    'aiokafka==0.4.2',
    'uuid==1.30',
    'Flask==1.0.2',
    'colorama==0.4.0',
    'mongoengine==0.15.3',
    'redis==2.10.6',
    'geopy==1.17.0',
    'jsonmerge==1.5.1']
)