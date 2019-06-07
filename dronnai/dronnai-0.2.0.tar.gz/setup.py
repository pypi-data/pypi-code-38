from setuptools import setup

setup(
    name='dronnai',
    version='0.2.0',
    description='Neural Networks Training Center by Dronn.com',
    url='https://bitbucket.org/inboxliberatorteam/gym/src/master/',
    author='Dronn AI Team',
    author_email='info@dronn.com',
    # license='MIT',
    packages=['dronnai'],
    install_requires=[
        'numpy',
        'pandas',
        'torch',
        'torchtext',
        'spacy',
        'scikit-learn',
        'tqdm',
        'flatten_dict',
        'sacred',
        'tensorboardX'
      ],
      zip_safe=False)
