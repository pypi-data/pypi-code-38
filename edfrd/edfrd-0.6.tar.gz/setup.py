# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['edfrd']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0']

setup_kwargs = {
    'name': 'edfrd',
    'version': '0.6',
    'description': 'edfrd is a Python 3 software library to read EDF files.',
    'long_description': "# edfrd\n\nedfrd is a Python 3 software library to read EDF files.\n\n## Installation\n\n```bash\npip3 install --user edfrd\n```\n\n## Usage\n\n```python\nfrom edfrd import read_header, read_data_records\n\nfile_path = 'PATH/TO/FILE.edf'\n\nheader = read_header(file_path, calculate_number_of_data_records=True)\n\ndata_records = [\n    data_record for data_record in\n    read_data_records(file_path, header)  # generator\n]\n\nfor signal_header, signal in zip(header.signals, data_records[0]):\n    print(\n        signal_header.label,\n        signal.size,\n        signal.dtype  # numpy int16 array\n    )\n\n# optional parameters, default is None\n_ = read_data_records(\n    file_path,\n    header,\n    start=0,\n    end=header.number_of_data_records\n)\n```\n",
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://cbmi.htw-berlin.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
