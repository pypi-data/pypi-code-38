import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.set-top-box",
    version="1.0.1",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard for set-top box testobjects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.set_top_box'],
    install_requires=[
        'testwizard.core==1.0.1',
        'testwizard.testobjects-core==1.0.1',
        'testwizard.commands-audio==1.0.1',
        'testwizard.commands-mobile==1.0.1',
        'testwizard.commands-powerswitch==1.0.1',
        'testwizard.commands-remotecontrol==1.0.1',
        'testwizard.commands-video==1.0.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)








