from setuptools import setup, find_packages

setup(name='postgresql-deepgeo',
      version='0.0.1',
      url='https://github.com/Sotaneum/PostgreSQL-DeepGeo',
      license='MIT',
      author='Donggun LEE',
      author_email='gnyotnu39@gmail.com',
      description='Easy Deep Learning',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False,
      setup_requires=['tensorflow-gpu==1.9.0','exifread','piexif','pillow','matplotlib','scikit-image','IPython','keras','cython','deepgeo'],
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ]
)
