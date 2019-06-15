# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gingerit']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'gingerit',
    'version': '0.7.0',
    'description': 'Correcting spelling and grammar mistakes based on the context of complete entences. Wrapper around the gingersoftware.com API',
    'long_description': "===============================\nGingerit\n===============================\n\n.. image:: https://badges.gitter.im/Join%20Chat.svg\n   :alt: Join the chat at https://gitter.im/Azd325/gingerit\n   :target: https://gitter.im/Azd325/gingerit?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge\n\n.. image:: https://img.shields.io/travis/Azd325/gingerit.svg\n        :target: https://travis-ci.org/Azd325/gingerit\n\n.. image:: https://img.shields.io/pypi/v/gingerit.svg\n        :target: https://pypi.python.org/pypi/gingerit\n\n\nCorrecting spelling and grammar mistakes based on the context of complete sentences. Wrapper around the gingersoftware.com API\n\n* Free software: MIT license\n* Documentation: https://gingerit.readthedocs.org.\n\nInstallation:\n-------------\n\n::\n\n    pip install gingerit\n\nUsage:\n------\n\n::\n\n    from gingerit.gingerit import GingerIt\n\n    text = 'The smelt of fliwers bring back memories.'\n\n    parser = GingerIt()\n    parser.parse(text)\n\nTODO:\n-----\n\n - More tests\n - Commandline Tool\n\nContributing:\n-------------\n\n1. Fork it\n2. Create your feature branch (`git checkout -b my-new-feature`)\n3. Commit your changes (`git commit -am 'Add some feature'`)\n4. Push to the branch (`git push origin my-new-feature`)\n5. Create new Pull Request\n\nThanks\n------\n\nThank you for [Ginger Proofreader](http://www.gingersoftware.com/) for such awesome service. Hope they will keep it free :)\n\nThanks to @subosito for this inspriration https://github.com/subosito/gingerice (Ruby Gem)\n",
    'author': 'Tim Kleinschmdit',
    'author_email': 'tim.kleinschmidt@gmail.com',
    'url': 'https://github.com/Azd325/gingerit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
