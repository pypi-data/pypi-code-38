from setuptools import setup, find_packages

setup(
    name='ppts',
    version='1.0.26',
    description='ppt with web',
    author='simdd',
    author_email='dev.simdd@gmail.com',
    packages=find_packages(),
    scripts=['bin.py'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ppts = bin:main',
        ]
    }
)
