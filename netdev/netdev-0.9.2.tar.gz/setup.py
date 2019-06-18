# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['netdev',
 'netdev.vendors',
 'netdev.vendors.arista',
 'netdev.vendors.aruba',
 'netdev.vendors.cisco',
 'netdev.vendors.fujitsu',
 'netdev.vendors.hp',
 'netdev.vendors.infotecs',
 'netdev.vendors.juniper',
 'netdev.vendors.mikrotik',
 'netdev.vendors.terminal',
 'netdev.vendors.ubiquiti']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0', 'asyncssh>=1.15,<2.0']

extras_require = \
{'docs': ['sphinx>=2.0,<3.0', 'sphinx_rtd_theme>=0.4,<0.5']}

setup_kwargs = {
    'name': 'netdev',
    'version': '0.9.2',
    'description': 'Asynchronous multi-vendor library for interacting with network devices',
    'long_description': 'Netdev\n******\n\nAsynchronous multi-vendor library for interacting with network devices\n\nInspired by netmiko\n\nRequires:\n---------\n* asyncio\n* AsyncSSH\n* Python >=3.5\n* pyYAML\n  \n \nSupports: \n---------\n* Cisco IOS \n* Cisco IOS XE\n* Cisco IOS XR\n* Cisco ASA\n* Cisco NX-OS \n* HP Comware (like V1910 too)\n* Fujitsu Blade Switches\n* Mikrotik RouterOS\n* Arista EOS\n* Juniper JunOS\n* Aruba AOS 6.X\n* Aruba AOS 8.X\n* Terminal\n\nExamples:\n---------\nExample of interacting with Cisco IOS devices:\n\n.. code-block:: python\n\n    import asyncio\n    import netdev\n\n    async def task(param):\n        async with netdev.create(**param) as ios:\n            # Testing sending simple command\n            out = await ios.send_command("show ver")\n            print(out)\n            # Testing sending configuration set\n            commands = ["line console 0", "exit"]\n            out = await ios.send_config_set(commands)\n            print(out)\n            # Testing sending simple command with long output\n            out = await ios.send_command("show run")\n            print(out)\n            # Testing interactive dialog\n            out = await ios.send_command("conf", pattern=r\'\\[terminal\\]\\?\', strip_command=False)\n            out += await ios.send_command("term", strip_command=False)\n            out += await ios.send_command("exit", strip_command=False, strip_prompt=False)\n            print(out)\n\n\n    async def run():\n        dev1 = { \'username\' : \'user\',\n                 \'password\' : \'pass\',\n                 \'device_type\': \'cisco_ios\',\n                 \'host\': \'ip address\',\n        }\n        dev2 = { \'username\' : \'user\',\n                 \'password\' : \'pass\',\n                 \'device_type\': \'cisco_ios\',\n                 \'host\': \'ip address\',\n        }\n        devices = [dev1, dev2]\n        tasks = [task(dev) for dev in devices]\n        await asyncio.wait(tasks)\n\n\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(run())\n\n\n',
    'author': 'Sergey Yakovlev',
    'author_email': 'selfuryon@gmail.com',
    'url': 'https://netdev.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
