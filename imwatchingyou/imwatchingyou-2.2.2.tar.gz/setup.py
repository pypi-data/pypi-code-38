import setuptools

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''


setuptools.setup(
    name="imwatchingyou",
    version="2.2.2",
    author="PySimpleGUI",
    author_email="mike@PySimpleGUI.org",
    install_requires=['PySimpleGUI', ],
    description="A Python GUI-based Python debugger enabling realtime watching and modification of variables and expressions, plus a REPL-light",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords="GUI UI PySimpleGUI tkinter",
    url="https://github.com/PySimpleGUI/imwatchingyou",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
    ),
)