import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcmcAllotter",
    version="0.1.0b1",
    author="Saurabh Kumar",
    author_email="saurabhkm@hotmail.com",
    description="Solve allottment problems with MCMC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saurabhkm/mcmcAllotter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Intended Audience :: Education',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='matching, allottment, mcmc, markovChainMonteCarlo',
    install_requires=['numpy', 'pandas'],
)