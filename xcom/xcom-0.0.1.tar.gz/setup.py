from setuptools import setup

with open('version.txt') as f:
    ver = f.read().strip()

setup(
    name='xcom',
    version=ver,
    description='Simulator',
    author='Vinogradov Dmitry',
    author_email='dgrapes@gmail.com',
    license='MIT',
    packages=['xcom', 'xcom.modbus'],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
