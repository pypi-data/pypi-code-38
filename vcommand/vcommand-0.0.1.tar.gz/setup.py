import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="vcommand",
    version="0.0.1",
    author="Zak H.",
    author_email="zhandricken@bridgew.edu",
    description="A simple framework for building voice-controlled applications.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/zakarh/vcommand",
    packages=setuptools.find_packages(),
    set_requires=[
        'PyAudio',
        'pyttsx3',
        'speech_recognition',
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Other OS",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation",
        "Topic :: Home Automation",
    ],
)
