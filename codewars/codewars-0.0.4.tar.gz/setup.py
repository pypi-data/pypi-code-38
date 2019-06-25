import setuptools

with open("README.MD", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="codewars", # codewars when updating to pip
    version="0.0.4",
    author="Annihilator708",
    author_email="",
    description="A toolbox for daily use. This is just a toolbox to make my life easier. Maybe yours too..",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 1 - Planning"
    ],
    install_requires=[
        'backcall',
        'decorator',
        'ipython',
        'ipython-genutils',
        'jedi',
        'parso',
        'pexpect',
        'pickleshare',
        'prompt-toolkit',
        'ptyprocess',
        'Pygments',
        'scapy',
        'six',
        'traitlets',
        'WCWidth',
        'PyBluez',
        'scapy'
    ],
    python_requires='>=3.6.*',
    include_package_data=True,
    zip_safe=False
)