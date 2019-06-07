import subprocess
import collections
import json
import sys
import os

required_packages=collections.OrderedDict()
required_packages['requests']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.21.0", "pip_error": "", "description": ""}
required_packages['adodbapi']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.6.0.7", "pip_error": "https://pypi.org/simple/adodbapi/ only lists 2.6.0.7 so maybe we have to use that instead of 2.0", "description": "A pure Python package implementing PEP 249 DB-API using Microsoft ADO."}
required_packages['asn1crypto']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.24.0", "description": "Fast ASN.1 parser and serializer with definitions for private keys, public keys, certificates, CRL, OCSP, CMS, PKCS#3, PKCS#7, PKCS#8, PKCS#12, PKCS#5, X.509 and TSP"}
required_packages['autoitlibrary3']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.1.post1", "description": ""}
required_packages['bcrypt']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.1.6", "description": "Modern password hashing for your software and your servers"}
required_packages['beautifulsoup4']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.7.1", "description": "Screen-scraping library"}
required_packages['certifi']={"pip_working": True, "nexus_pkg_available": True, "version": "==2019.3.9", "description": "Python package for providing Mozilla's CA Bundle."}
required_packages['cffi']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.12.3", "description": "Foreign Function Interface for Python calling C code."}
required_packages['chardet']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.0.4", "description": "Universal encoding detector for Python 2 and 3"}
required_packages['chromedriver']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.24.1", "description": ""}
required_packages['collections2']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.3.0", "description": "A set of improved data types inspired by the standard library's collections module"}
required_packages['cx-oracle']={"pip_working": True, "nexus_pkg_available": True, "version": "==7.1.3", "description": "Python interface to Oracle"}
required_packages['datetime']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.3", "description": ""}
required_packages['decorator']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.4.0", "description": "Better living through Python with decorators"}
required_packages['dialogs']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.14", "description": "Handles natural language inputs and outputs on cognitive robots"}
required_packages['docutils']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.14", "description": "Docutils -- Python Documentation Utilities"}
required_packages['et-xmlfile']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.0.1", "description": "An implementation of lxml.xmlfile for the standard library"}
required_packages['faker']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.0.7", "description": "Faker is a Python package that generates fake data for you."}
required_packages['idna']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.8", "description": "Internationalized Domain Names in Applications (IDNA) - wanted 2.2 initially but conflict with requests version"}
required_packages['ipaddress']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.0.22", "description": "IPv4/IPv6 manipulation library"}
required_packages['jdcal']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.4.1", "description": "Julian dates from proleptic Gregorian and Julian calendars."}
required_packages['jenkinsapi']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.3.9", "description": "A Python API for accessing resources on a Jenkins continuous-integration server."}
required_packages['jsonpatch']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.23", "description": "Apply JSON-Patches (RFC 6902)"}
required_packages['jsonpointer']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.0", "description": "Library to resolve JSON Pointers according to RFC 6901"}
required_packages['ldap3']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.6", "description": "ldap3 is a strictly RFC 4510 conforming LDAP V3 pure Python client library. The same codebase runs in Python 2, Python 3, PyPy and PyPy3"}
required_packages['lxml']={"pip_working": True, "version": "==4.3.3", "pip_error": "Could not find function xmlCheckVersion in library libxml2. Is libxml2 installed?", "description": "Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API.", "nexus_pkg_available": True}
required_packages['multi-key-dict']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.0.3", "description": "Multi key dictionary implementation"}
required_packages['natsort']={"pip_working": True, "nexus_pkg_available": True, "version": "==6.0.0", "description": "Simple yet flexible natural sorting in Python."}
required_packages['openpyxl']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.6.2", "description": "A Python library to read/write Excel 2010 xlsx/xlsm files"}
required_packages['paramiko']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.4.2", "pip_error": "Problems installing Cryptography", "description": "SSH2 protocol library"}
required_packages['pathlib2']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.3.3", "description": "Object-oriented filesystem paths"}
required_packages['pbr']={"pip_working": True, "nexus_pkg_available": True, "version": "==5.2.0", "description": "Python Build Reasonableness"}
required_packages['pexpect']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.7.0", "description": "Pexpect allows easy control of interactive console applications."}
required_packages['ptyprocess']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.6.0", "description": "Run a subprocess in a pseudo terminal"}
required_packages['pyasn1']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.4.5", "description": "ASN.1 types and codecs. ", "pip_error": "pyasn1-modules requires pyasn1-0.4.5 instead of 0.1.9"}
required_packages['pyasn1-modules']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.2.5", "description": ""}
required_packages['pycparser']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.19", "description": "C parser in Python"}
required_packages['pycryptodome']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.8.1", "description": "Cryptographic modules for Python."}
required_packages['pygments']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.4.0", "description": "Pygments is a syntax highlighting package written in Python."}
required_packages['pynacl']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.3.0", "description": "Python binding to the Networking and Cryptography (NaCl) library", "pip_error": "make utility is missing from path"}
required_packages['pyopenssl']={"pip_working": True, "nexus_pkg_available": True, "version": "==19.0.0", "pip_error": "Problems installing Cryptography", "description": "Cryptographic modules for Python."}
required_packages['pypubsub']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.3.0", "description": "Python Publish-Subscribe Package", "pip_error": "Version 4.0.0 not available"}
required_packages['pyrfc']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.1.2", "description": "Implementation of some RFC standard algorithms. Now Include RFC2548 RFC2759 RFC3078 RFC3079"}
required_packages['python-dateutil']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.8.0", "description": "The dateutil module provides powerful extensions to the standard datetime module, available in Python."}
required_packages['python-jenkins']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.4.0", "description": ""}
required_packages['pywin32']={"pip_working": True, "nexus_pkg_available": True, "version": "==224", "description": "Python extensions for Microsoft Windows Provides access to much of the Win32 API, the ability to create and use COM objects,and the Pythonwin environment.", "pip_error": "Our pip can't find it in our Nexus although it's there"}
required_packages['robotframework']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.1.1", "description": ""}
required_packages['robotframework-archivelibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.4.0", "description": "Robot Framework keyword library for handling ZIP files"}
required_packages['robotframework-autoitlibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.2.4", "description": ""}
required_packages['robotframework-databaselibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.2", "description": "Database utility library for Robot Framework"}
required_packages['robotframework-excellib']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.1.0", "description": "This test library provides some keywords to allow opening, reading, writing and saving Excel files from Robot Framework."}
required_packages['robotframework-faker']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.2.0", "description": ""}
required_packages['robotframework-httplibrary3']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.6.0", "description": ""}
required_packages['robotframework-requests']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.5.0", "description": "Robot Framework keyword library wrapper around requests"}
required_packages['robotframework-ride']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.7.3.1", "description": "Robot Framework is a generic test automation framework for acceptance level testing. RIDE is a lightweight and intuitive editor for Robot Framework test data."}
required_packages['robotframework-seleniumlibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.3.1", "description": ""}
required_packages['robotframework-selenium2library']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.0.0", "description": ""}
required_packages['robotframework-sshlibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.3.0", "description": "", "pip_error": "Depends on PyNaCl and Cryptography"}
required_packages['robotframework-stringformat']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.1.8", "description": "StringFormat is a string formatter for Robot Framework. This library is a python .format() wrapper."}
required_packages['robotframework-sudslibrary3']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.9", "description": ""}
required_packages['selenium']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.141.0", "description": "Python language bindings for Selenium WebDriver"}
required_packages['setuptools']={"pip_working": True, "nexus_pkg_available": True, "version": "==41.0.1", "description": "SetupTools."}
required_packages['six']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.12.0", "description": "Python 2 and 3 compatibility utilities"}
required_packages['slate3k']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.5.3", "description": "Slate is a Python package that simplifies the process of extracting text from PDF files. It depends on the PDFMiner package.", "pip_error": "depends on distribute"}
required_packages['suds2']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.7.1", "description": ""}
required_packages['suds-jurko']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.6", "description": ""}
required_packages['tlslite']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.4.9", "description": "tlslite implements SSL and TLS."}
required_packages['typing']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.6.6", "description": "Type Hints for Python"}
required_packages['wxpython']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.0.4", "description": "Cross platform GUI toolkit for Python, \"Phoenix\" version", "pip_error": "Depends on Pypubsub"}
required_packages['xlrd']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.2.0", "description": "Library for developers to extract data from Microsoft Excel (tm) spreadsheet files"}
required_packages['xlutils']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.0.0", "description": "Utilities for working with Excel files that require both xlrd and xlwt"}
required_packages['xlwt']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.3.0", "description": "Library to create spreadsheet files compatible with MS Excel 97/2000/XP/2003 XLS files, on any platform, with Python 2.6, 2.7, 3.3+"}
required_packages['wheel']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.33.4", "description": ""}
#required_packages['robotframework-sikulilibrary']={"pip_working": False, "version": "==1.0.5", "description": "Sikuli Robot Framework Library provide keywords for Robot Framework to test UI through Sikuli.", "pip_error": "Read Timeout in pip and browser, Nexus seems to have speed and reliability issues. When failed after 4 timeouts, serves 404 for 10-20 seconds before working again"}

from setuptools import setup
			
def pkg_list():
	a=[]
	for package in required_packages:
		a.append(package+required_packages[package]['version'])
	return a

setup(name='rft-core',
      version='0.4.0',
      description='RobotFramework Toolkit',
      url='https://github.com/ludovicurbain/rft-core.git',
      author='Ludovic Urbain',
      author_email='ludovic.urbain@swift.com',
      license='MIT',
      packages=['rft-core'],
	  install_requires=[
          pkg_list(),
      ],
      zip_safe=False)