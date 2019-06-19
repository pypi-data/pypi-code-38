# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_markdown_messaging', 'django_markdown_messaging.migrations']

package_data = \
{'': ['*'], 'django_markdown_messaging': ['templates/messaging/*']}

install_requires = \
['django>=2.2,<3.0', 'markdown>=2.6,<3.0']

setup_kwargs = {
    'name': 'django-markdown-messaging',
    'version': '0.1.0',
    'description': 'Django application to create messages based on markdown',
    'long_description': '# Django messaging application\n\nThis messaging app has to be integrated into an existing django website.\n\n## Quick start\n\n1. Add "messaging" to your INSTALLED_APPS setting like this:\n```\nINSTALLED_APPS = [  \n    ...  \n    \'django_markdown_messaging\',  \n]\n```\n\n2. Include the messaging URLconf in your project urls.py like this:\n```\npath(\'msg/\', include((\'django_markdown_messaging.urls\', \'messaging\'))),\n```\n\n3. Run `python manage.py migrate` to create the messaging models.\n\n4. Start the development server and visit http://127.0.0.1:8000/msg to check if everything is ok.\n\n## How to use\n\n1. Go to http://127.0.0.1:8000/msg and click on "new message"\n2. Write your message using plain text or markdown syntax\n3. You can choose to allow editing or deleting of this message\n4. Then, click on "Save" button\n5. Link of the message appears on screen, just copy and paste it to your friends! :-)\n6. If you go on the message page, you\'ll see your message and eventually a link to edit or delete this message.\n\n## Override those ugly templates\n\nYou can add a *templates/messaging* folder in your base application to override default templates.\n\nThere are four pages that you can override safely:\n- **[base.html](https://gitlab.com/aloha68/django-markdown-messaging/blob/master/django_markdown_messaging/templates/messaging/base.html)**: the base page for all the messaging templates\n- **[index.html](https://gitlab.com/aloha68/django-markdown-messaging/blob/master/django_markdown_messaging/templates/messaging/index.html)**: index page with a form to search a message\n- **[message.html](https://gitlab.com/aloha68/django-markdown-messaging/blob/master/django_markdown_messaging/templates/messaging/message.html)**: page to display an existing message\n- **[edit-message.html](https://gitlab.com/aloha68/django-markdown-messaging/blob/master/django_markdown_messaging/templates/messaging/edit-message.html)**: page to add a new message or to edit an existing one\n\nIf you have any questions, I can help you! :-)\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-markdown-messaging',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
