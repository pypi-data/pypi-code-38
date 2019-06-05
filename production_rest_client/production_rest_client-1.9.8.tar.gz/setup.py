from setuptools import setup, find_packages
 
setup(
    name = 'production_rest_client',
    version = '1.9.8',
    keywords = ['runner', 'client'],
    description = 'REST Runner',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
      ],
    license = 'MIT License',
	url = 'https://pypi.org/project/production_rest_client',
    install_requires = ['simplejson>=1.1'],
 
    author = 'weili.han',
    author_email = '826338726@qq.com',
    
    packages = find_packages(),
    platforms = 'any',
)