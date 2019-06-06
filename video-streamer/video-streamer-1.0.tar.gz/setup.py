#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="video-streamer",
    version="1.0",
    author="Artur Pietrzyk, Tomasz Kolbusz",
    author_email="artudi54@gmail.com, tomaszkolbusz1@gmail.com",
    description="Client-server video streaming application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/artudi54/video_streamer",
    packages=find_packages(),
    package_data={"": ["*.ui", "*.png", "*.qrc", "*.rcc"],
                  "vstreamer": ["resources/*", "resources/icons/*"]},
    scripts=["bin/video_streamer.py", "bin/video_streamer_server.py",
             "bin/video_streamer_setter.py"],
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux"],
)
