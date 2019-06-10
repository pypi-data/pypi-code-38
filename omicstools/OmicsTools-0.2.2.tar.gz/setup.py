from setuptools import setup, find_packages

setup(
    name='OmicsTools',
    packages=find_packages(),
    version='0.2.2',
    url='https://github.com/fraenkel-lab/OmicsTools',
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],
    license='MIT',
    author='iamjli',
    author_email='iamjli@mit.edu',
    description='',
    install_requires=[
        "pandas==0.24.2", 
        "numpy==1.16.4",
        "networkx",
        "mygene", 
        "goenrich"
    ]
)