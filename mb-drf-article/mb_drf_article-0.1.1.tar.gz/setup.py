# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mb_drf_article']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mb-drf-article',
    'version': '0.1.1',
    'description': 'An article model for Django-Rest-Framework.',
    'long_description': '# Mb-drf-article\n\nMb-drf-article is a simple Django Rest Framework app to add some articles.\n\n## Quick start\n\n### 1. Add "mb-drf-article" to your `INSTALLED_APPS` settings\n\n```python\n# settings.py\n\nINSTALLED_APPS = [\n...\n\'mb-drf-article\',\n]\n```\n\n### 2. Include the articles URLconf in your project `urls.py`\n\n```python\n# urls.py\n\nurlpatterns = [\n    # ...\n    path(\'articles/\', include(\'mb-drf-article.urls\')),\n]\n```\n\n### 3. Add the models in your Database\n\nRun `python manage.py migrate` in your SHELL.\n\n### 4. Update the Django Rest Framework Settings\n\nUpdate the Django Rest Framework settings to add a pagination.\n\n```python\n# Django Rest Framework\n# https://www.django-rest-framework.org\n\nREST_FRAMEWORK = {\n    # ...\n    \'DEFAULT_PAGINATION_CLASS\': (\'rest_framework.pagination.\'\n                                 \'LimitOffsetPagination\'),\n    \'PAGE_SIZE\': 5\n}\n```\n',
    'author': 'mikael briolet',
    'author_email': 'mikaelbriolet.services@gmail.com',
    'url': 'https://github.com/8area8/drf-articles',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
