# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_static_markdown_blog',
 'django_static_markdown_blog.core',
 'django_static_markdown_blog.migrations']

package_data = \
{'': ['*'],
 'django_static_markdown_blog': ['static/blog/css/*',
                                 'static/blog/js/*',
                                 'templates/blog/*']}

install_requires = \
['beautifulsoup4>=4.6,<5.0',
 'django>=2.2,<3.0',
 'libaloha>=0,<1',
 'markdown>=2.6,<3.0',
 'redis>=2.10,<3.0']

setup_kwargs = {
    'name': 'django-static-markdown-blog',
    'version': '0.1.0',
    'description': 'Django application to create a blog based on local Markdown files',
    'long_description': '# Django static Markdown blog\n\nThe purpose of this application is to provide an Internet blog based on local files. Those files can be Markdown formatted to add some style to your notes. This app has to be integrated into an existing django website.\n\n## Quick start\n\n1. Add "django_static_markdown_blog" to your INSTALLED_APPS setting like this:\n```\nINSTALLED_APPS = [  \n    ...  \n    \'django_static_markdown_blog\',\n]\n```\n\n2. In the settings file, add two variables\n```\nBLOG_FOLDER = \'/tmp/markdown-files/\'\nBLOG_INDEX_FILE = \'main.md\'\n```\n\n3. Include the django_static_markdown_blog URLconf in your project urls.py like this:\n```\npath(\'blog/\', include((\'django_static_markdown_blog.urls\', \'blog\'))),\n```\n\n4. It is useless to migrate database because it is based on local files\n\n5. Start the development server and visit http://127.0.0.1:8000/blog to check if everything is ok.\n\n## How to use\n\nTo use the software, you must have defined the variable *BLOG_FOLDER* which indicates the name of the directory where the Markdown files are located, as well as the variable *BLOG_MAIN_FILE* which corresponds to the main file of each directory (it is possible to create an unlimited tree structure).\n\n### Write your first page\n\nYour first file is the one at the root of the *BLOG_FOLDER* directory and must be named as the *BLOG_MAIN_FILE* variable. This is the entry point of your blog, the page seen by your visitors when they arrive on your blog.\n\nTo write a Markdown file, the principle is very simple. It is divided into two parts separated by at least one empty line. The first part contains the metadata of the file which are filled a little lower. The second part is the content of your page, formattable with Markdown.\n\nThere is an exemple of a home page:\n\n    title: Welcome on my blog\n\n    Hello everyone, and welcome to my **blog**. \n    Feel free to visit my project page on [PyPI](https://pypi.org/project/django-static-markdown-blog/) or directly on [GitLab](https://gitlab.com/aloha68/django-static-markdown-blog/).\n\n    Enjoy your visit!\n\n### Supported metadata\n\nThere is the full list of the supported metadata:\n\n- **title**: set the title of your page\n- **date**: set a custom date for your page, else we will use the datetime of the file\n- **groups**: define a group list that can access the page. It means that unauthorized people will not see the page\n- **icons**: define an icon that will be display in the article list for a page\n\n',
    'author': 'Aloha68',
    'author_email': 'dev@aloha.im',
    'url': 'https://gitlab.com/aloha68/django-static-markdown-blog',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
