
from distutils.core import setup

def getFile():
    with open('README.rst') as f:
        return f.read()

setup(
    name='stockAnalysis',        
    packages=['stockAnalysis'],  
    version='1.4.1',     
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=getFile(),
    author='Sadik Erisen',                  
    author_email='fserisen@gmail.com',      
    url='https://github.com/francose/stockAnalysis',
    download_url='https://github.com/francose/stockAnalysis/archive/master.zip',
    keywords=['stocks', 'finance', 'market', 'S&P500', 'yahoo'],
    install_requires=[            
        'attrs == 19.1.0'
        'beautifulsoup4 == 4.7.1'
        'certifi == 2018.11.29'
        'chardet == 3.0.4'
        'colorama == 0.4.1'
        'configparser == 3.7.4'
        'crayons == 0.2.0'
        'cycler == 0.10.0'
        'idna == 2.8'
        'idna-ssl == 1.1.0'
        'kiwisolver == 1.0.1'
        'multidict == 4.5.2'
        'numpy == 1.16.1'
        'pandas == 0.24.1'
        'pyparsing == 2.3.1'
        'python-dateutil == 2.8.0'
        'pytz == 2018.9'
        'requests == 2.21.0'
        'six == 1.12.0'
        'soupsieve == 1.8'
        'typing-extensions == 3.7.2'
        'yarl == 1.3.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
