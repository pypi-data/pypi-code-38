import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zmqflp",
    version="0.8.3",
    author="Curtis Wang",
    author_email="ycwang@u.northwestern.edu",
    description="PyZMQ server/client implementing asyncio freelance protocol based on Min RK's starter code",
    packages=setuptools.find_packages(),
    install_requires=['pyzmq', 'cbor2'],
    url="https://github.com/curtywang/zmqflp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking"
    ],
)