# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snippet_image']

package_data = \
{'': ['*']}

install_requires = \
['pillow>=5.2,<7.0']

setup_kwargs = {
    'name': 'snippet-image',
    'version': '0.1.6',
    'description': 'Package for simple creation images of snippets for social networks using pillow. Pictures for snippets can be inserted for sharing pages in social networks, for example in tag meta:',
    'long_description': '============================\nsnippet-image\n============================\n\nPackage for simple creation images of snippets for social networks using pillow_.\n\n.. _pillow: https://pillow.readthedocs.io/en/stable/\n\nPictures for snippets can be inserted for sharing pages in social networks, for example in tag meta:\n\n.. code-block:: html\n\n    <meta property="og:image" content="Link to your snippet image" />\n    <meta name="twitter:image" content="Link to your snippet image" />\n\nInstallation\n---------------------------\n\n`pip3 install snippet-image`\n\nUser guide\n---------------------------\n\nTo start creating images for snippets, it is enough to import the function ```from snippet_image import create_snippet_image```.\n\n.. code-block:: python\n\n    from snippet_image import create_snippet_image\n\n    image_blob = create_snippet_image(\n            font=\'/home/iamterminator/.fonts/OpenSans-Bold.ttf\', # Path to your font file\n            font_size=62, # Font size\n            background=\'/home/iamterminator/.wallpapers/jakethedog.jpg\', # Path to your background image\n            size=(1200, 630), # Size of snippet image. (width, height)\n            text=\'Jake the Dog\', # Text for draw on snippet image\n            brightness=0.3, # Brightness of background\n        )\n\n    with open(\'jake-the-dog-snippet-image.jpg\', \'wb\') as file:\n        file.write(image_blob.getvalue())\n\nIntegration\n--------------------\n\nDjango: `django-snippet-image`_.\n\nWagtail: `wagtail-snippet-image`_.\n\n.. _django-snippet-image: https://github.com/acrius/django-snippet-image\n\n.. _wagtail-snippet-image: https://github.com/acrius/wagtail-snippet-image\n\nRead more on home_.\n\n.. _home: https://github.com/acrius/snippet-image.\n',
    'author': 'acrius',
    'author_email': 'acrius@mail.ru',
    'url': 'https://github.com/acrius/snippet-image',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
