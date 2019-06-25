import setuptools
VERSION = '0.0.1'
with open('requirements.txt') as f:
    PACKAGES = f.read().splitlines()
with open("README.md", "r") as fh:
    README = fh.read()
setuptools.setup(
    name='flask-app',
    version=VERSION,
    author="Kimbugwe Simon Peter",
    author_email="kimbsimon2@gmail.com",
    install_requires=PACKAGES,
    description="A tool to create flask boilerplate code",
    long_description=README,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'flask-app=flask_app.__main__:main'
        ]
    },
    url="https://github.com/kimbugp/flask_app",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
