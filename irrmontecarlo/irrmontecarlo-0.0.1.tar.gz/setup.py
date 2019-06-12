
import setuptools



setuptools.setup(
    name="irrmontecarlo",
    version="0.0.1",
    author="Jack Treanor",
    author_email="jftreanor@gmail.com",
    description="Framework for simulating IRR of a portfolio via FOREX Monte Carlo",
    url="https://github.com/jftreanor/IRRMonteCarlo",
    packages=setuptools.find_packages(),
    install_requires=['numpy','scipy','matplotlib','pandas'],
    dependency_links=['https://github.com/python/cpython/blob/3.7/Lib/random.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    

)
