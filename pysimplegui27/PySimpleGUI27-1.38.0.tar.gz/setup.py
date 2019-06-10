import setuptools

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''


setuptools.setup(
    name="PySimpleGUI27",
    version="1.38.0",
    author="MikeTheWatchGuy",
    author_email="mike@PySimpleGUI.com",
    description="Python 2.7 version of PySimpleGUI - GUI SDK Launched in 2018 Actively developed and supported. Super-simple to create custom GUI's.  Python 2.7 & 3 Support. 100 Demo programs & Cookbook for rapid start. Extensive documentation. Examples using Machine Learning(GUI, OpenCV Integration,  Chatterbot), Rainmeter Style Floating Desktop Widgets, Matplotlib + Pyplot integration, add GUI to command line scripts, PDF & Image Viewer. Great for beginners as well as advanced GUI programmers",
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=['future'],
    keywords="GUI UI tkinter wrapper simple easy beginner novice student graphics progressbar progressmeter",
    url="https://github.com/MikeTheWatchGuy/PySimpleGUI",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
    ),
)