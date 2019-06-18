from setuptools import setup, find_packages

setup(

    name='hello curtis',
    version='1.1.1',
    description='a hello curtis project',
    url='https://github.com/odhiambocuttice/myfirstproject',
    author='odhiambo cuttice',
    author_email='odhiambocuttice@gmail.com',

    classifiers=[

            'License :: OSI Approved :: MIT License',
         'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
    ],

    keywords='hello curtis setuptools development',

    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['requests'],

)
