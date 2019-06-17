import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mworks',
    version='1.0.0',
    author="msm",
    package_dir={'mworks': 'src'},
    packages=['mworks'],
    description="A common utility framework for web microservices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "prometheus-flask-exporter",
        "flask",
        "mistune",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
