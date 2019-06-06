from distutils.core import setup
setup(
  name = 'NonCipher',
  packages = ["NonCipher"],
  version = '2.2',
  license='Apache 2.0',
  description = 'XOR Algorithm with hashing, wow!',
  # long_description=open('README.md','rt').read(),
  # long_description_content_type='text/markdown',
  author = 'NonSense',
  author_email = 'valerastatilko@gmail.com',
  url = 'https://github.com/NotStatilko/NonCipher',
  download_url = 'https://github.com/NotStatilko/NonCipher/archive/2.0.tar.gz',
  keywords = ['Python', 'Cipher', 'Hashing', 'XOR'],

  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Security :: Cryptography',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ]
)
