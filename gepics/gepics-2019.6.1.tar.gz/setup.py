from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gepics',
    version='2019.6.1',
    url="https://github.com/michel4j/gepics",
    license='MIT',
    author='Michel Fodje',
    author_email='michel4j@gmail.com',
    description='Python GObject Wrapper for EPICS Process Variables',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='epics gobject development',
    py_modules=['gepics'],
    install_requires=['pyepics'],
    classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
