from setuptools import setup, find_packages

setup(name='tf_assist',   #pip install tf_assist
      version='0.1.4',
      description='Deep Learning library on top of Tensorflow for fast prototyping',
      url='http://github.com/aniketmaurya/tf_assist',
      author='Aniket Maurya',
      author_email='aniketmaurya.ai@gmail.com',
      license='MIT',
      packages= find_packages(),      #import assist
      install_requires=['numpy'],      
      zip_safe=False,

      classfiers=[
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6'
      ])