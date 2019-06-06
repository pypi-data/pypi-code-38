import setuptools
from util.arguments import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='clicmod',
    version=version,
    author='Nick Corso-passaro',
    author_email='Nick.Corso-Passaro@ipsoft.com',
    description="A command line interface for IPsoft 1Desk content management.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://dtools.ipsoft.com/bitbucket/projects/CO/repos/1desk-impex/browse',
    license='MIT',
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ['clicmod = impex.impex:main']
    },
    install_requires=[
        'requests',
        'urllib3',
        'pyfiglet',
        'tqdm'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
