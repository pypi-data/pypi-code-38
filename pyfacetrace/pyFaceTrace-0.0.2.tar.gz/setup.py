from setuptools import setup, find_packages
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: Microsoft',
    'Programming Language :: Python :: 3.6',
    #'Topic :: Internet :: Proxy Servers',
    #'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
]

setup(
    name = 'pyFaceTrace',      
    version = '0.0.2',
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    author = 'funny4875',        
    author_email = 'funny4875@gmail.com',
    url = 'https://github.com/funny4875/pyFaceTrace',
	description = 'face trace tool',
	license='MIT',
	include_package_data=True,
	entry_points={
	'console_scripts': ['predictVedio=pyFaceTrace:predictVedio','getPicFromCam=pyFaceTrace:getPicFromCam']
		}
    )