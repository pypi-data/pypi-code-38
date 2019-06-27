import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="vlibras-translate",
    version="1.0.3",
    author="MoraesCaio (LAVID-UFPB)",
    author_email="caiomoraes.cesar@gmail.com",
    description="VLibras (LAVID-UFPB) translation module for translating brazilian portugues to LIBRAS.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.vlibras.gov.br/",
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'vlibras-translate=vlibras_translate.translation:main',
            'vlibras-translate-file=vlibras_translate.file_translation:main'
        ],
    },
    install_requires=[
        'nltk',
        'unidecode',
        'py4j',
        'pygtrie',
        'pyparsing',  # sem esse pacote funciona, mas lança um warning
        'psutil',
        'hunspell',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Portuguese (Brazilian)",
    ],
)
