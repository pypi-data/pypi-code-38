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
    'version': '2.0.1',
    'description': 'Simple helpers to interface to JIRA from an API or command line.',
    'long_description': 'Some simple API functions and command-line tools for interacting with JIRA.\n\n\nSetup\n-----\nAll the tools and functions here need your specific information from\na ``jira.config`` file in your home directory, so you have to do this setup\nbefore anything can be used:\n\n* run ``jira-example-config --install`` to install an example config file\n  (you can run it without ``--install`` to see the contents of what would be\n  installed. (If you already have a ``jira.config`` in your home directory,\n  this script will `not` overwrite it.)\n* Fill out the values in the config file with your appropriate data\n  (see the comments in that file for guidance).\n\n\nCommand-Line Tools\n------------------\n\n``jira-example-config`` can install an example config file for you, see above.\n\n``jira-make-linked-issue`` makes a new JIRA issue that is linked to an exisiting issue;\nthe new issue\'s fields can be set from defaults in your ``jira.config``\nor those values can be overridden on the command line.\nSee ``--help`` on this command for all the command line options,\nand the comments in ``jira.config`` for setting the defaults.\n\n``jira-add-comment`` adds a comment to a JIRA issue.\nThe ``jira.config`` file is needed to authenticate to JIRA.\nNo other data from the ``jira.config`` file is used by this commmand.\nSee ``--help`` on this command for details. You can also use ``-`` as your comment\nand ``jira-add-comment`` will read the comment from stdin instead. Note that if you\nuse ``-`` interactively, you cannot edit your comment before it is posted.\n\n``jira-search-issues`` searches JIRA using your JQL query.\nThe ``jira.config`` file is needed to authenticate to JIRA.\nYou may set a default integer max_results value\nas ``MAX_RESULT_COUNT`` in ``jira.config``,\nor set a value of ``-1`` for no max by default.\nSee ``--help`` on this command for details.\n\n``jira-link-issues`` creates a link between two issues.\nThe ``jira.config`` is needed to authenticate to JIRA.\n\n\n``jira-update-assignee`` changes the assignee of the JIRA to the provided user.\n\n\nError Logging Tools\n-------------------\n\nThese functions are designed to be used within Python code\nto assist with various error commenting logic.\n\n* ``jiratools.error_logging.add_jira_error_comment`` can take an error\n  and add a formatted comment to a relevant JIRA issue\n\n* ``jiratools.error_logging.add_jira_comment_with_table`` can add a comment\n  with a formatted data table to a jira issue\n\n* ``jiratools.error_logging.update_jira_for_errors`` can check found errors\n  against a list of JIRA issues\n  and add comments to any JIRA issues where a match is found.\n\n\nFormatting Tools\n----------------\n\nThese functions are designed to be used within Python code\nto assist with comment formatting logic.\n\n* ``jiratools.formatting.format_autoupdate_jira_msg`` takes a message body\n  and add relevant title/header data\n\n* ``jiratools.formatting.format_as_jira_table`` takes headers and table rows\n  and formats a JIRA-style table\n\n\nExamples\n~~~~~~~~\n\n* ``jira-add-comment JIRA-1234 "Work in Progress. PR delayed by network problems."``\n  -- Add the comment to JIRA-1234 using the user/password from your ``jira.config``\n  Note that the comment has to be just one command line argument surrounded by quotes\n  if it contains spaces, etc.\n* ``jira-make-linked-issue JIRA-1234``\n  -- will create a JIRA in your ``TEST_PROJECT`` to test JIRA-1234,\n  and link the two, assigning it to you and\n  adding any watchers specified in your default watchers list.\n* ``jira-make-linked-issue JIRA-1234 --project OTHER``\n  -- will create a test JIRA as above, but in ``OTHER``\n* ``jira-make-linked-issue JIRA-1234 --user bobm5523``\n  -- will create the JIRA as above, but assign to ``bobm5523``\n* ``jira-make-linked-issue JIRA-1234 -w sall9987 -w benj4444``\n  -- will create the JIRA and assign ``sall9987`` and ``benj4444`` as watchers\n  instead of your default watcher list\n* ``jira-search-issues "project=ABC AND summary ~ client"``\n  -- will print a list of links and titles for issues in project ABC\n  that include the word "client" in the summary.\n* ``jira-link-issues ABC-123 XYZ-456``\n  -- will create a link such that ``ABC-123`` relates to ``XYZ-456``\n',
    'author': 'Brad Brown',
    'author_email': 'brad@bradsbrown.com',
    'url': 'https://github.com/jolly-good-toolbelt/jiratools/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
