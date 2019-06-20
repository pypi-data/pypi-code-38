import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MICTI",
    version="0.1.3",
    author="Nigatu Ayele",
    author_email="naodm2006awet4@gmail.com",
    description="Feature extraction approach in single-cell gene expression profiling for cell-type marker identification.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/insilicolife/micti",
    packages=setuptools.find_packages(), 
    install_requires=['numpy', 'pandas','scipy','scikit-learn', 'matplotlib','mpl_toolkits','pylab','gensim', 'gprofiler', 'seaborn','pyensembl', 'bs4','urllib','requests','json',"setuptools"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
    
)
