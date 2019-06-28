from setuptools import setup

with open("README.md", "r") as readme:
    description = readme.read()

with open("LICENSE", "r") as readme:
    license_x = readme.read()

setup(
    name='jangli',
    version='1.1.0',
    packages=['jangli'],
    url='https://github.com/AbhimanyuHK/Json_Object_Conv',
    license='MIT License',
    author='Abimanyu H K',
    author_email='manyu1994@hotmail.com',
    description='Convert json to python object and vice versa ',
    long_description=description,
    long_description_content_type="text/markdown"
)
