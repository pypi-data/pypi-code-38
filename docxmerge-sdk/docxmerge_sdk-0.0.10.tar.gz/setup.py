import setuptools

setuptools.setup(
    name="docxmerge_sdk",
    version="0.0.10",
    author="David viejo pomata",
    author_email="davidviejopomata@gmail.com",
    description="Sdk for docxmerge",
    url="https://github.com/Docxmerge/docxmerge-sdk",
    packages=['docxmerge_sdk'],
    package_dir={
        'docxmerge_sdk': 'docxmerge_sdk'
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
    ],

)
