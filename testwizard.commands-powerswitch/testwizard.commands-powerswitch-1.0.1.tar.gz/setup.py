import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.commands-powerswitch",
    version="1.0.1",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard Powerswitch commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.commands_powerswitch'],
    install_requires=[
        'testwizard.commands-core==1.0.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)








