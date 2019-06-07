# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['xnat_access']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'xnat-access',
    'version': '0.3',
    'description': 'XNAT Access.',
    'long_description': "# XNAT Access\n\nThin XNAT REST API wrapper for Python 3 requests.\n\n\n## Installation\n\n```bash\npip3 install --user xnat-access\n```\n\n\n## Usage\n\n```python\nfrom xnat_access import XNATClient\n\nxnat = XNATClient(\n    'https://example.com/xnat',\n    'USERNAME',\n    'PASSWORD'\n)\n\nurl = 'projects/PROJECT/subjects/SUBJECT/experiments/EXPERIMENT/scans'\nscans = xnat.get_result(url)\nprint(scans)\n\n# all functions\n# --------------------\n# xnat.get_request\n# xnat.get_json\n# xnat.get_result\n# xnat.get_file\n# xnat.download_file\n# xnat.put_request\n# xnat.upload_file\n# xnat.delete_request\n# xnat.open_session\n# xnat.close_session\n# xnat.session_is_open\n```\n",
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://cbmi.htw-berlin.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
