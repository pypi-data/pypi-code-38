import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pySpeechAlien",
    version="2.1",
    author="Arpan Sahoo",
    author_email="asahoo1@jhu.edu",
    description="Speech analysis tool",
    long_description=long_description,
    url="https://github.com/arpansahoo/pySpeechAlien",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    keywords='praat speech-analysis python',
    install_requires=[
      'numpy>=1.15.2',
      'praat-parselmouth>=0.3.2',
      'pandas>=0.23.4',
      'scipy>=1.1.0',
      ],
    packages=['pySpeechAlien'],
    zip_safe=False,
)
