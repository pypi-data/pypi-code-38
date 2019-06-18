# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jiratools']

package_data = \
{'': ['*']}

install_requires = \
['jira>=2.0,<3.0']

entry_points = \
{'console_scripts': ['jira-add-comment = jiratools:_cli_add_comment',
                     'jira-example-config = jiratools:_example_config_install',
                     'jira-link-issues = jiratools:cli_jira_link',
                     'jira-make-linked-issue = '
                     'jiratools:_create_test_jira_from',
                     'jira-search-issues = jiratools:_cli_search',
                     'jira-update-assignee = jiratools:_change_jira_assignee']}

setup_kwargs = {
    'name': 'jiratools',
    'version': '2.0.0',
    'description': 'Simple helpers to interface to JIRA from an API or command line.',
    'long_description': None,
    'author': 'Brad Brown',
    'author_email': 'brad@bradsbrown.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
