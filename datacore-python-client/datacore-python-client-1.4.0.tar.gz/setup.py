import setuptools


# Define version easier up here.
version = "1.4.0"


setuptools.setup(
    name='datacore-python-client',
    version=version,
    description='Extensible Python Client for accessing datacore RESTfully',
    url='https://github.com/Bodaclick/datacore-python-client',
    author='Vincent Medina',
    author_email='vincent@everymundo.com',
    packages=['datacore'],
    install_requires=[
        "requests"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
      ],
    keywords="em datacore everymundo",
    zip_safe=False
)
