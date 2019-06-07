# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ocpp', 'ocpp.v16']

package_data = \
{'': ['*'], 'ocpp.v16': ['schemas/*']}

install_requires = \
['jsonschema>=3.0,<4.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

setup_kwargs = {
    'name': 'ocpp',
    'version': '0.2.0',
    'description': 'Python package implementing the JSON version of the Open Charge Point Protocol (OCPP).',
    'long_description': '[![CircleCI](https://circleci.com/gh/mobilityhouse/ocpp/tree/master.svg?style=svg)](https://circleci.com/gh/mobilityhouse/ocpp/tree/master)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ocpp.svg)\n\n# OCPP\n\nPython package implementing the JSON version of the Open Charge Point Protocol (OCPP). Currently\nonly OCPP 1.6 is supported.\n\n## Installation\n\nYou can either install from Pypi:\n\n``` bash\n$ pip install ocpp\n```\n\nOr install the package by running:\n\n``` bash\n$ pip install .\n```\n\n## Usage\n\nBelow you can find examples on how to create a simple charge point as well as a charge point.\n\n**Note**: to run these examples the dependency `websockets` is required! Install it by running:\n\n``` bash\n$  pip install websockets\n```\n\n### Central system\n\n``` python\nimport asyncio\nimport websockets\nfrom datetime import datetime\n\nfrom ocpp.routing import on\nfrom ocpp.v16 import ChargePoint as cp\nfrom ocpp.v16.enums import Action, RegistrationStatus\nfrom ocpp.v16 import call_result\n\n\nclass ChargePoint(cp):\n    @on(Action.BootNotification)\n    def on_boot_notitication(self, charge_point_vendor, charge_point_model, **kwargs):\n        return call_result.BootNotificationPayload(\n\t    current_time=datetime.utcnow().isoformat(),\n\t    interval=10,\n\t    status=RegistrationStatus.accepted\n\t)\n\n\nasync def on_connect(websocket, path):\n    """ For every new charge point that connects, create a ChargePoint instance\n    and start listening for messages.\n\n    """\n    charge_point_id = path.strip(\'/\')\n    cp = ChargePoint(charge_point_id, websocket)\n\n    await cp.start()\n\n\nasync def main():\n    server = await websockets.serve(\n        on_connect,\n        \'0.0.0.0\',\n        9000,\n        subprotocols=[\'ocpp1.6\']\n    )\n\n    await server.wait_closed()\n\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\n### Charge point\n\n``` python\nimport asyncio\nimport websockets\n\nfrom ocpp.v16 import call, ChargePoint as cp\nfrom ocpp.v16.enums import RegistrationStatus\n\n\nclass ChargePoint(cp):\n    async def send_boot_notification(self):\n        request = call.BootNotificationPayload(\n            charge_point_model="Optimus",\n            charge_point_vendor="The Mobility House"\n        )\n\n        response = await self.call(request)\n\n        if response.status ==  RegistrationStatus.accepted:\n            print("Connected to central system.")\n\n\nasync def main():\n    async with websockets.connect(\n        \'ws://localhost:9000/CP_1\',\n         subprotocols=[\'ocpp1.6\']\n    ) as ws:\n\n        cp = ChargePoint(\'CP_1\', ws)\n\n        await asyncio.gather(cp.start(), cp.send_boot_notification())\n\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\n# License\n\nExcept from the documents in `docs/v16/specification/` everything is licensed under [MIT](LICENSE).\n[© The Mobility House](https://www.mobilityhouse.com/int_en/).\n\nThe documents in `docs/v16/specification/` are licensed under Creative Commons\nAttribution-NoDerivatives 4.0 International Public License.\n',
    'author': 'Auke Willem Oosterhoff',
    'author_email': 'aukewillem.oosterhoff@mobilityhouse.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
