from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='guardpost-oidc',
      version='0.0.1',
      description='Classes to use OpenID Connect authentication with GuardPost.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='https://github.com/RobertoPrevato/GuardPost-OpenIDConnect',
      author='RobertoPrevato',
      author_email='roberto.prevato@gmail.com',
      keywords='authentication openid connect oidc',
      license='MIT',
      packages=['guardpost-oidc'],
      install_requires=['guardpost',
                        'pyjwt'],
      include_package_data=True,
      zip_safe=False)
