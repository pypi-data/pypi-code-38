#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='tkgtools',
    version='0.19.6.2',
    description=(
        'tkgtools is created by George Zhao, who is working for NOKIA, 2010-2012, 2014-2019.\n This lib is used for implementing algorithm in 3GPP 35.206, f1, f2, f3, f4, f5, f1* and f5*'
    ),
    long_description="""
===================
Introduction
===================
tkgtools is a library which is used as a base for 3GPP security architecture.

tkg is stands for 3GPP Key Generator.

Only f1, f2, f3, f4, f5, f1* and f5* are supported in this library.

tkgtools is written on python 3.6.5, python 2 is not supported.

===================
Author
===================
George Zhao who is working for Nokia in 2010-2012, 2014-2019.

maito: georgezhao_1980@163.com

===================
How to get it
===================

::

	pip install tkgtools

===================
Functions
===================
f1(key, rand, sqn, amf, op, mac_a, opc = [])

  key(list of int), length 16
  
  rand(list of int), length 16
  
  sqn(list of int), length 6
  
  amf(list of int), length 2
  
  op(list of int), length 16
  
  mac_a(list of int), length 8
  
  opc(list of int), length 6, it is an optional parameter, if opc is set, f1 function will never use op parameter, and use opc to instead.
  
  mac_a is used as a return value.

  
f2345(key, rand, op, res, ck, ik , ak, opc = [])

  key(list of int), length 16
  
  rand(list of int), length 16
  
  op(list of int), length 16
  
  res(list of int), length 8
  
  ck(list of int), length 16
  
  ik(list of int), length 16
  
  ak(list of int), length 6
  
  opc(list of int), length 6, it is an optional parameter, if opc is set, f2345 function will never use op parameter, and use opc to instead.
  
  res, ck, ik, and ak are used as return values.
  
  
f1star(key, rand, sqn, amf, op, mac_s, opc = [])

  key(list of int), length 16
  
  rand(list of int), length 16
  
  sqn(list of int), length 6
  
  amf(list of int), length 2
  
  mac_s(list of int), length 8
  
  opc(list of int), length 6, it is an optional parameter, if opc is set, f1star function will never use op parameter, and use opc to instead.
  
  mac_s is used as a return value.	
  

f5star(key, rand, op, ak, opc = [])

  key(list of int), length 16
  
  rand(list of int), length 16
  
  op(list of int), length 16
  
  ak(list of int), length 6
  
  opc(list of int), length 6, it is an optional parameter, if opc is set, f5star function will never use op parameter, and use opc to instead.
  
  ak is used as return value.

All test data could be retrieved in 3GPP 35.207

===================
Example
===================
::

	from tkgtools import tkgtools
	
	key = [0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11]
	op = [0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x10,0x11,0x12,0x13,0x14,0x15,0x16]
	rand = [0x16,0x2a,0x9b,0x8c,0x46,0x9a,0xdc,0x1f,0x41,0xcc,0x69,0x73,0xee,0xe5,0x9e,0xaf]
	res=[0 for col in range(8)]
	ck=[0 for col in range(16)]
	ik=[0 for col in range(16)]
	ak=[0 for col in range(6)]
	tkgtools.f2345(key, rand, op, res, ck, ik, ak)
	
===================
Any problem
===================
Please contact georgezhao_1980@163.com
""",
    author='George Zhao',
    author_email='georgezhao_1980@163.com',
    maintainer='George Zhao',
    maintainer_email='georgezhao_1980@163.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='http://not-available.now',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)