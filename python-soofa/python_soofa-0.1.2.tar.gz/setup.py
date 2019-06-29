from distutils.core import setup
setup(
  name = 'python_soofa',
  packages = ['python_soofa'],
  version = '0.1.2',
  license='MIT',
  description = 'Python package to simplify integration to soofapay',
  author = 'Soofapay Team',
  author_email = 'info@soofapay.com',
  url = 'https://github.com/soofapay/python-soofa',
  download_url = 'https://github.com/soofapay/python-soofa/archive/v0.1.2-alpha.tar.gz',
  keywords = ['soofa', 'soofapay', 'pay', "python"],
  install_requires=[
          'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)