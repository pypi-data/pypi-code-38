__version__ = "0.1.1"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ttsbroker",
    version=__version__,
    author='Altertech Group',
    author_email="pr@altertech.com",
    description="Simple TTS (Text-To-Speech) broker for Python",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/alttch/ttsbroker",
    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    install_requires=['sounddevice', 'soundfile', 'requests'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ),
)
