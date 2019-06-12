import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Actifio",
    version="1.0.1",
    author="Kosala Atapattu",
    author_email="kosala.atapattu@actifio.com",
    description="Actifio Restful API wrapper for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Actifio/actifio-python-package",
    packages=['Actifio'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
      'urllib3'
    ]
)
