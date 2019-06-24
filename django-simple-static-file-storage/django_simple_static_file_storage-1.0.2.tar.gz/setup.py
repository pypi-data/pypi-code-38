from setuptools import setup, find_packages


with open('VERSION.txt') as f:
    version = f.readline()


setup(
    name='django_simple_static_file_storage',
    version=version,
    url='https://github.com/matix-io/django-simple-static-file-storage',
    license='MIT',
    description='Simple static file storage for user uploads.',
    long_description='',
    author='Connor Bode',
    author_email='connor@matix.io',  # SEE NOTE BELOW (*)
    packages=find_packages(),
    install_requires=[],
    zip_safe=False,
    classifiers=[],
)
