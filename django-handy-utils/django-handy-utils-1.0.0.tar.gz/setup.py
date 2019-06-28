from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='django-handy-utils',
    version='1.0.0',
    packages=['django_handy_utils'],
    url='https://github.com/mfdeux/django-handy-utils',
    license='MIT',
    author='Marc Ford',
    author_email='mrfxyz567@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['django'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
