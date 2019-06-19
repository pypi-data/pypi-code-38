# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_ping_me', 'django_ping_me.migrations']

package_data = \
{'': ['*'],
 'django_ping_me': ['templates/ping_me/*', 'templates/ping_me/partials/*']}

install_requires = \
['django-cron==0.5.1',
 'django>=2.2,<3.0',
 'libaloha>=0,<1',
 'markdown>=2.6,<3.0']

setup_kwargs = {
    'name': 'django-ping-me',
    'version': '0.1.0',
    'description': 'Django application to create availability statistics of web servers',
    'long_description': '# Django ping-me application\n \nThis app has to be integrated into an existing django website.\n\nThe purpose of this application is to establish an HTTP connection with a web server list in order to make availability statistics.\n\n## Quick start\n\n1. Add "ping-me" to your INSTALLED_APPS setting like this:\n```\nINSTALLED_APPS = [  \n    ...  \n    \'django_ping_me\',\n]\n```\n\n2. Include the ping-me URLconf in your project urls.py like this:\n```\npath(\'ping-me/\', include((\'django_ping_me.urls\', \'ping_me\'))),\n```\n\n3. Run `python manage.py migrate` to create models.\n\n4. Start the development server and visit http://127.0.0.1:8000/ping-me to check if everything is ok.\n\n## Override those ugly templates\n\nYou can add a *templates/ping_me* folder in your base application to override default templates.\n\nHave a look on [default templates](https://gitlab.com/aloha68/django-ping-me/tree/master/django_ping_me/templates/ping_me) to see how to override them.\nKeep in mind that some features (like edit or delete a server) use *bootstrap* popups and AJAX calls.\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-ping-me',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
