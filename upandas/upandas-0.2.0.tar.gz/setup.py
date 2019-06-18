# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['upandas']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=0.24,<0.25', 'uncertainties>=3.1,<4.0']

setup_kwargs = {
    'name': 'upandas',
    'version': '0.2.0',
    'description': 'Handle uncertainties within pandas dataframes and series',
    'long_description': "# upandas\n\nupandas makes it easy to use quantities with uncertainties in pandas DataFrames and Series.\n\nupandas relies on the excellent [uncertainties]() package, and of course [pandas](). \n\n```python\n# A dataframe with nominal values in columns x and y,\n# and their respective uncertainties in u_x, u_y\n\nIn [1]: n=3; df = pd.DataFrame({ 'x': randn(n),  'u_x': 0.1*rand(n),\n   ...:                   'y': randn(n), 'u_y': 0.1*rand(n) })\n\nIn [2]: df\nOut[2]:\n          x       u_x         y       u_y\n0 -1.735288  0.014020 -1.426411  0.093879\n1 -0.677756  0.084329 -1.254212  0.034601\n2  2.410181  0.054435 -1.611307  0.020315\n\n# Convert col/u_col pairs to uarray columns\nIn [3]: uf = separate_to_u(df)\nIn [4]: uf\nOut[4]:\n                x               y\n0  -1.735+/-0.014    -1.43+/-0.09\n1    -0.68+/-0.08  -1.254+/-0.035\n2     2.41+/-0.05  -1.611+/-0.020\n\n# Operate on columns in the DataFrame as usual,\n# but propagate the uncertainties\nIn [5]: uf['xy2'] = uf['x'] * uf['y']**2\nIn [6]: uf\nOut[6]:\n                x               y           xy2\n0  -1.735+/-0.014    -1.43+/-0.09    -3.5+/-0.5\n1    -0.68+/-0.08  -1.254+/-0.035  -1.07+/-0.15\n2     2.41+/-0.05  -1.611+/-0.020   6.26+/-0.21\n\n# Convert back to a conventional dataframe\n# for e.g. storage to HDF5.\nIn [17]: u_to_separate(uf)\nOut[17]:\n          x       u_x         y       u_y       xy2     u_xy2\n0 -1.735288  0.014020 -1.426411  0.093879 -3.530698  0.465620\n1 -0.677756  0.084329 -1.254212  0.034601 -1.066143  0.145112\n2  2.410181  0.054435 -1.611307  0.020315  6.257576  0.211830\n```\n\n## Getting Started\n\n### Prerequisites\n\nupandas relies on uncertainties and pandas,\nbut pip will install these if needed. \n\n### Installing\n\n```\npip install upandas\n```\n\n## Running the tests\n\nBasic tests are included, using [pytest](https://docs.pytest.org/en/latest/index.html). In the base directory:\n```\npytest tests \n```\nor just `make test`.\n\n## Usage\n\nupandas so far provides only two functions:\n\n- `separate_to_u(df)`: converts col, u_col pairs to a uarray column col.\n- `u_to_separate(df)`: converts a uarray column col to a pair col, u_col.\n\nIf applied to a Series, these functions look at the 'row' index rather than columns.\n\n## Built With\n\n- [poetry](https://poetry.eustace.io/)\n\nNote that as a 'modern' python project and uses [pyproject.toml](pyproject.toml) rather than setuptools `setup.py`.\n\nIf you want to develop locally, pull this repository and execute... TBC.\n\n## Contributing\n\nPlease do send me pull requests!\n\n## Versioning\n\nWe use [SemVer](http://semver.org/) for versioning. \n\n## Authors\n\n- *Lincoln Turner* - [lincolndturner](https://bitbucket.org/lincolndturner)\n\n## TODO\n\n- MultiIndex support.\n- Make ufloats a pandas [extensions type](https://pandas.pydata.org/pandas-docs/stable/development/extending.html#extension-types), although not clear this is needed.\n- Make uarrays a pandas [https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.api.extensions.ExtensionArray.html#pandas.api.extensions.ExtensionArray] extension array, although again not clear if this is needed.\n- Register pandas [custom accessors](https://pandas.pydata.org/pandas-docs/stable/development/extending.html#registering-custom-accessors), so that we can be a bit more pythonic about the conversion: `df.u.from_separate()...`,\n- ... and `df.u.nomnal_values`, `df.u.std_devs`.\n- More tests\n\n## License\n\nThis project is licensed under the Monash/BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.\n\n## Acknowledgments\n\nInspired by the extensive support of uncertainties \nin [lyse](https://bitbucket.org/labscript_suite/lyse/),\nas part of the [labscript suite](http://labscriptsuite.org/).\n",
    'author': 'Lincoln Turner',
    'author_email': 'lincoln.turner@monash.edu',
    'url': 'https://bitbucket.org/lincolndturner/upandas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
