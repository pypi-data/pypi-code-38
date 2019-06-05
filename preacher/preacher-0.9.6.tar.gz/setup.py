# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['preacher',
 'preacher.app',
 'preacher.app.cli',
 'preacher.compilation',
 'preacher.core',
 'preacher.presentation']

package_data = \
{'': ['*']}

install_requires = \
['pyhamcrest>=1.9,<2.0',
 'pyjq>=2.3,<3.0',
 'requests>=2.21,<3.0',
 'ruamel.yaml>=0.15.89,<0.16.0']

entry_points = \
{'console_scripts': ['preacher-cli = preacher.app.cli.main:main']}

setup_kwargs = {
    'name': 'preacher',
    'version': '0.9.6',
    'description': 'A web API verification tool.',
    'long_description': '========\nPreacher\n========\n\n.. image:: https://img.shields.io/badge/python-3.7+-blue.svg\n    :target: https://www.python.org/\n.. image:: https://badge.fury.io/py/preacher.svg\n    :target: https://badge.fury.io/py/preacher\n.. image:: https://travis-ci.org/ymoch/preacher.svg?branch=master\n    :target: https://travis-ci.org/ymoch/preacher\n.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/ymoch/preacher\n.. image:: https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg\n    :target: https://lgtm.com/projects/g/ymoch/preacher/context:python\n\nPreacher verifies API servers,\nwhich requests to API servers and verify the response along to given scenarios.\n\nScenarios are written in `YAML`_ and `jq`_ queries\nso that any developers can write without learning toughly.\n\n\nUsage\n=====\n\nRequirements\n------------\nSupports only Python 3.7+.\n\n.. code-block:: sh\n\n    pip install preacher\n    preacher-cli scenario.yml\n\n    # Help command is available.\n    preacher-cli --help\n\n\nWriting Your Own Scenarios\n==========================\n\nExample\n-------\nHere is a simple configuration example.\n\n.. code-block:: yaml\n\n    label: Scenario example\n    default:\n      request:\n        path: /path\n    cases:\n      - label: Simple\n        request: /path/to/foo\n        response:\n          status_code: 200\n          body:\n            - describe: .foo\n              should:\n                equal: bar\n      - label: A Little Complecated\n        request:\n          path: /path/to/foo\n          params:\n            key1: value\n            key2:\n              - value1\n              - value2\n        response:\n          status_code:\n            - be_greater_than_or_equal_to: 200\n            - be_less_than: 400\n          body:\n            - describe:\n                jq: .foo\n              should:\n                - start_with: x\n                - end_with: y\n\nGrammer\n-------\n\nScenario\n********\nA ``Scenario`` is written in `YAML`_.\nA ``Scenario`` is a mapping that consists of below:\n\n- label: ``String`` (Recommended)\n    - A label of this scenario.\n    - This field is actually optional but recommended to tell this scenario from another.\n- default: ``Default`` (Optional)\n    - Default of this scenario.\n- cases: ``List<Case>``\n    - Test cases.\n\nCase\n****\nA ``Case`` is a mapping that consists of below:\n\n- label: ``String`` (Recommended)\n    - A label of this case.\n    - This field is actually optional but recommended to tell this case from another.\n- request: ``Request`` (Optional)\n    - A request.\n- response: ``ResponseDescription`` (Optional)\n    - A response description.\n\nRequest\n*******\nA ``Request`` is a mapping or a string.\n\nA mapping for ``Request`` has items below:\n\n- path: ``String`` (Optional)\n    - A request path. The default value is ``\'\'``.\n- params: ``Mapping<String, String>`` (Optional)\n    - Query parameters as a mapping of keys to values.\n\nWhen given a string, that is equivalent to ``{"path": it}``.\n\nResponse Decription\n*******************\nA ``ResponseDescription`` is a mapping that consists of below:\n\n- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)\n    - Predicates that match a status code as an integer value.\n    - When given a number, that is equivalent to ``{"equal": it}``.\n- body: ``Description`` or ``List<Description>`` (Optional)\n    - Descriptions that descript the response body.\n\nDescription\n***********\nA ``Description`` is a mapping that consists of below:\n\n- describe: ``String`` or ``Extraction``\n    - An extraction process.\n    - When given a string, that is equivalent to ``{"jq": it}``.\n- should: ``Predicate``, or ``List<Predicate>>`` (Optional)\n    - Predicates that match the extracted value.\n\nExtraction\n**********\nAn ``Extraction`` is a mapping or a string.\n\nA mapping for ``Extraction`` has one of below:\n\n- jq: ``String``\n    - A `jq`_ query.\n\nWhen fiven a string, that is equivalent to ``{"jq": it}``.\n\nPredicate\n*********\nA ``Predicate`` is a ``Matcher`` (can be extended in the future).\n\nMatcher\n*******\nA ``Matcher`` is a string or a mapping.\n\nAllowed strings are:\n\n- be_null\n- not_be_null\n- be_empty\n\nA mapping for ``Matcher`` has an item. Allowed items are:\n\n- be: ``Value`` or ``Matcher``\n    - Matches when it matches the given value or the given matcher.\n    - When given ``Value``, that is equivalent to ``{"equal": it}``.\n- not: ``Value`` or ``Matcher``\n    - Matches when it doesn\'t match the given value or the given matcher.\n    - When given ``Value``, that is equivalent to ``{"not": {"equal": it}}``\n- equal: ``Value``\n    - Matches when it equals the given value.\n- have_length: ``Integer``\n    - Matches when it has a length and its length is equal to the given value.\n- be_greater_than: ``Comparable``\n    - Matches when it is greater than the given value (it > argument).\n- be_greater_than_or_equal_to: ``Comparable``\n    - Matches when it is greater than or equal to the given value (it >= argument).\n- be_less_than: ``Comparable``\n    - Matches when it is less than the given value (it < argument).\n- be_less_than_or_equal_to: ``Comparable``\n    - Matches when it is less than or equal to the given value (it < argument).\n- contain_string: ``String``\n    - Matches when it is an string and contains the given value.\n- start_with: ``String``\n    - Matches when it is an string and starts with the given value.\n- end_with: ``String``\n    - Matches when it is an string and ends with the given value.\n- match_regexp: ``String``\n    - Matches when it is an string and matches the given regular expression.\n- have_item: ``Value`` or ``Matcher``\n    - Matches when it is a collection and has the given item.\n    - When given ``Value``, that is equivalent to ``{"equal": it}``.\n\nDefault\n*******\nA ``Default`` is a mapping that consists of below:\n\n- request: ``Request`` (Optional)\n    - A request to override the default request values.\n\n\n.. _YAML: https://yaml.org/\n.. _jq: https://stedolan.github.io/jq/\n.. _pipenv: https://pipenv.readthedocs.io/\n',
    'author': 'Yu Mochizuki',
    'author_email': 'ymoch.dev@gmail.com',
    'url': 'https://github.com/ymoch/preacher',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
