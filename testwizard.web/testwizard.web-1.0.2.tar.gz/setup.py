import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.web",
    version="1.0.2",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard for Web testobjects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.web'],
    install_requires=[
        'testwizard.core==1.0.2',
        'testwizard.testobjects-core==1.0.2',
        'testwizard.commands-audio==1.0.2',
        'testwizard.commands-video==1.0.2',
        'testwizard.commands-web==1.0.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)









