from setuptools import setup, find_packages

setup(name='geoviz',
      version='0.5',
      description='Wrapper to easily make geo-based visualizations',
      long_description='See [tutorial](https://locusanalytics.github.io/files/geoviz_tutorial.html)',
      long_description_content_type = 'text/markdown',
      url='https://github.com/LocusAnalytics/geoviz',
      author='W. Aaron Lee',
      author_email='alee@locus.co',
      license='MIT',
      packages=['geoviz', 'geoviz.data'],
      include_package_data=True,
      install_requires=['pandas',
                        'matplotlib',
                        'bokeh',
                        'geopandas',
                        'descartes',
                        'pysal',
                        'us',
                        "importlib_resources; python_version<'3.7'"
                        ])
