# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['isim']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'isim',
    'version': '0.7.0',
    'description': 'Python wrapper around the simctl utility',
    'long_description': '# isim\n\nThis is a Python wrapper around the `xcrun simctl` utility that Apple provides for interacting with the various Xcode developer tools. \n\n`xcrun simctl` is the tool for interacting with the iOS simulator and is the main focus of this module. The syntax is designed to remain as close to that which would be used on the command line as possible. For example, to list all runtimes on the command line you would do:\n\n    xcrun simctl list runtimes\n\nWith this module you can simply do:\n\n    from isim import Runtime\n    print(Runtime.list_all())\n\nMost functions are on the item that they affect. So instead of running something on a device like:\n\n    xcrun simctl do_thing <DEVICE_ID> arg1 arg2 ...\n\nYou can do this:\n\n    from isim import Device\n    iPhone7 = Device.from_name("iPhone 7")\n    iPhone7.do_thing(arg1, arg2, ...)\n\n## Testing\n\nTo run the tests, all you need to do is run `python -m pytest tests` from the root directory.\n',
    'author': 'Dale Myers',
    'author_email': 'dale@myers.io',
    'url': 'https://github.com/dalemyers/xcrun',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
