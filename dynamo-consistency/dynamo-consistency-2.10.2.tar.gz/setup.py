import glob
import setuptools

import dynamo_consistency

with open('README.rst', 'r') as fh:
    long_description = ''.join([
        line for line in fh if
        ':ref:' not in line
    ])

setuptools.setup(
    name='dynamo-consistency',
    version=dynamo_consistency.__version__,
    packages=setuptools.find_packages(),
    author='Daniel Abercrombie',
    author_email='dabercro@mit.edu',
    description='Consistency plugin for Dynamo Dynamic Data Management System',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SmartDataProjects/dynamo-consistency',
    install_requires=['pyyaml',
                      'docutils',
                      'MySQL-python',
                      'psutil',
                      'cmstoolbox>=0.14.2'],
    scripts=[s for s in glob.iglob('bin/*') if not s.endswith('~')],
    python_requires='>=2.6, <3',
    package_data={   # Test data for document building
        'dynamo_consistency': ['consistency_config.json',
                               'report_schema.sql',
                               'web/*']
        }
    )
