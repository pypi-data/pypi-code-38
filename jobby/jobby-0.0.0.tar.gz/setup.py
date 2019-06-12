import os
from setuptools import setup


def load_readme():
    with open('README') as f:
        readme = f.read()
    
    return readme


def load_requirements():
    with open('requirements.txt') as f:
        requirements = f.readlines()
    
    requirements = map(lambda r: r.strip(), requirements)
    requirements = filter(len, requirements)
    
    return list(requirements)


def get_jobby_data_files():
    data_files = list()
    
    package_dir = os.path.dirname(os.path.abspath(__file__))
    module_dir = os.path.join(package_dir, 'jobby')
    lib_dir = os.path.join(module_dir, 'lib')
    
    for root, dirs, filenames in os.walk(lib_dir):
        for filename in filenames:
            relative_filepath = os.path.join(
                os.path.relpath(root, module_dir), filename)
            data_files.append(relative_filepath)
    
    return data_files


setup(
    name='jobby',
    version='0.0.0',
    license='MIT',
    author='Nilaksh Das',
    url='http://github.com/nilakshdas/jobby',
    description='Runs jobs in the background',
    long_description=load_readme(),
    install_requires=load_requirements(),
    packages=['jobby'],
    include_package_data=True,
    package_data={'jobby': get_jobby_data_files()},
    entry_points={'console_scripts': ['jobby=jobby.cli:main']},
    zip_safe=False)
