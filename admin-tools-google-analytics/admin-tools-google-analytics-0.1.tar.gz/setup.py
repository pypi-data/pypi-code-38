from setuptools import setup, find_packages

setup(name='admin-tools-google-analytics',
      version='0.1',
      description='Django admin tools dashboard modules',
      long_description='Google analytics modules for django admin tools dashboard.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 2.2',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
      keywords='django admin-tools analytics dashboard module',
      url='https://github.com/17b0080/dat-google-analytics',
      author='17b0080',
      author_email='evdokimovma99@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'oauth2client==4.1.3',
          'google-api-python-client==1.7.9'
      ],
      include_package_data=True,
      zip_safe=False)