# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['slcp']
entry_points = \
{'console_scripts': ['slcp = slcp:main']}

setup_kwargs = {
    'name': 'slcp',
    'version': '0.1.0',
    'description': 'Copy all files with given extension from a directory and its subfolders to another directory.',
    'long_description': "# Selective Copy\n\nSimple command line application that copies all files with given extension from a directory and its subfolders to another directory showing progress bar and remaining files counter.\\\nAllows to preserve a source folder structure and to create a log if necessary.\\\nOpens a filedialog if source and/or destination are not given in the command line.\\\nCreates folders in a destination path if they don't exist.\n\n<pre>\nUsage: slcp ext [-s SRC] [-d DST] [-sc | -dc] [-p] [-l] [-h]\n\nPositional arguments:\next                     Extension of the files to copy, enter without a dot.\n\nOptional arguments:\n-s SRC, --source SRC    Source folder path.\n-d DST, --dest DST      Destination folder path.\n-sc, --srccwd           Use current working directory as a source folder.\n-dc, --dstcwd           Use current working directory as a destination folder.\n-p, --preserve          Preserve source folder structure.\n-l, --log               Create and save log to the destination folder.\n-h, --help              Show this help message and exit.\n</pre>\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details\n\n## Acknowledgments\n\nInspired by the task from [Chapter 9 of Automate the Boring Stuff](https://automatetheboringstuff.com/chapter9/).\n",
    'author': 'Kirill Plotnikov',
    'author_email': 'kpltnk@gmail.com',
    'url': 'https://github.com/pltnk/selective_copy',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
