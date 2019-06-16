from setuptools import setup, find_packages

setup(
      name = 'echidna_obj',
      version = '1.1.1',
      description = 'A Parser for 3D .obj data models (.obj file format) - working with ADENITA and SAMSON',
      url = 'https://gitlab.com/chris_h_/echidna',
      author = 'Christiane Huetter',
      author_email = 'christianevrhuetter@gmail.com',
      packages = find_packages(),
      license = 'MIT',
      install_requires = ['scikit-learn'],
      classifiers = [
            'Programming Language :: Python :: 3',
      ],
)

