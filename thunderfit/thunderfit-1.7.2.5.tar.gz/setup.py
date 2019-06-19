from setuptools import setup, find_packages

def readme():
    with open("README.rst") as f:
        return f.read()

setup(
    name='thunderfit',
    python_requires='>3.6',
    version='1.7.2.5',
    description='Thunderfit fitting code',
    long_description=readme(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords='raman analysis fitting',
    url='https://github.com/Mitchwatts93/thunderfit',
    author='https://github.com/Mitchwatts93',
    author_email='',
    license='MIT',
    packages=find_packages(),
    install_requires = ['jsonschema==2.6.0',
        'dill==0.2.9',
        'scipy==1.1.0',
        'numpy==1.15.1',
        'matplotlib==2.2.3',
        'pandas==0.23.4',
        'lmfit==0.9.13',
        'tqdm==4.26.0',
        'asteval==0.9.13',
        'typing==3.6.6',
        'imageio ==2.5.0',
        'sklearn == 0.0'
        ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        "console_scripts": ['ramananalyse = thunderfit.raman_routine:main', 'mapscan = thunderfit.map_scan:main',
                            'genparams = thunderfit.create_params:main']},
    )
