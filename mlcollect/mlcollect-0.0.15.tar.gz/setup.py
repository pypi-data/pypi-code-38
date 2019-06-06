import setuptools

setuptools.setup(
    name="mlcollect",
    version="0.0.15",
    author="Huynh Ngoc Sang",
    author_email="sanghuynhnt95@gmail.com",
    description="My machine learning collection",
    long_description="My machine learning collection",
    long_description_content_type="text/markdown",
    url="https://github.com/sanghuynh1501/mlcollect.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['tensorflow', 'matplotlib', 'sklearn', 'h5py']
)
