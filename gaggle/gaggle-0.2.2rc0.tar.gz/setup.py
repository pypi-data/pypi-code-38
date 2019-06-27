# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gaggle']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.5.3,<4.0.0',
 'google-api-python-client>=1.7.7,<2.0.0',
 'google-auth>=1.6.2,<2.0.0']

setup_kwargs = {
    'name': 'gaggle',
    'version': '0.2.2rc0',
    'description': 'aiohttp wrapper for google-api-client-python',
    'long_description': '# gaggle\n\nAn aiohttp-based Google API client.\n\nThe google-api-python-client requirement is because this library uses it to\ndiscover services and prepare requests, leveraging the prepare+execute pattern\nimplemented in googleapiclient.HttpRequest.\n\n## Usage\n\n### JSON\n\n```python\n\nimport asyncio\nimport aiohttp\nfrom gaggle import Client\n\n\nasync def main():\n    async with aiohttp.ClientSession() as session:\n        drive = Client(\n            session=session,\n            token=access_token,\n            # the following are optional and only required if the access_token is expired and can be refreshed\n            refresh_token=refresh_token,\n            client_id=client_id,\n            client_secret=client_secret\n        ).drive(\'v3\')\n        resp = await drive.files.list(q="parents in \'root\'")\n        # resp is an instance of aiohttp.ClientResponse\n        if resp.status == 200:\n            data = await resp.json()\n            files = data.get(\'files\', [])\n            for obj in files:\n                print(obj)\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(main())\n\n```\n\nResults in something like:\n```\n{\'kind\': \'drive#file\', \'id\': \'...\', \'name\': \'test.csv\', \'mimeType\': \'text/csv\'}\n{\'kind\': \'drive#file\', \'id\': \'...\', \'name\': \'Test Folder\', \'mimeType\': \'application/vnd.google-apps.folder\'}\n{\'kind\': \'drive#file\', \'id\': \'...\', \'name\': \'spreadsheet.xlsx\', \'mimeType\': \'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\'}\n{\'kind\': \'drive#file\', \'id\': \'...\', \'name\': \'spreadsheet\', \'mimeType\': \'application/vnd.google-apps.spreadsheet\'}\n```\n\n\n## Installation\n\n```\n$ pip install gaggle\n```\n\n## Testing and developing\n\nI\'ve included a handy Makefile to make these things fairly easy.\n\n```\n$ make setup\n$ make test\n```\n',
    'author': 'Steinn Eldjarn Sigurdarson',
    'author_email': 'steinnes@gmail.com',
    'url': 'https://github.com/steinnes/gaggle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
