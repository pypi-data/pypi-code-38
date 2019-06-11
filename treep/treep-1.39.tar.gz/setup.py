from setuptools import setup, find_packages, Extension

setup( name='treep',
       version='1.39',
       description='managing git projects structured in tree in python',
       long_description="see https://git-amd.tuebingen.mpg.de/amd-clmc/treep",
       classifiers=[
           'License :: OSI Approved :: MIT License',
           'Programming Language :: Python :: 2.7',
       ],
       keywords='project git tree',
       url='https://git-amd.tuebingen.mpg.de/amd-clmc/treep',
       author='Vincent Berenz',
       author_email='vberenz@tuebingen.mpg.de',
       license='GPL',
       packages=['treep'],
       install_requires=['lightargs','colorama','gitpython','argcomplete','pyyaml'],
       scripts=['bin/treep','bin/treep_to_yaml'],
       include_package_data=True,
       zip_safe=False
)



