from setuptools import setup

setup(
    name='LabelmeUtils',
    version='0.0.1',
    packages=['LabelmeUtils'],
    url='https://gitlab.com/futurefragment-pub/labelme-utils',
    license='MIT',
    author='sholto',
    author_email='sholto@futurefragment.com',
    description='Tool to decode labelme json payloads',
    install_requires=[
              'Pillow',
    ],
)
