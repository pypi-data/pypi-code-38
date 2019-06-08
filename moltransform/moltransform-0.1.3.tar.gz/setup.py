# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['moltransform']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0']

setup_kwargs = {
    'name': 'moltransform',
    'version': '0.1.3',
    'description': '',
    'long_description': '# moltransform 💻⚗️\n\n![PyPI - License](https://img.shields.io/pypi/l/moltransform.svg)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moltransform.svg)\n![PyPI](https://img.shields.io/pypi/v/moltransform.svg)\n![PyPI - Format](https://img.shields.io/pypi/format/moltransform.svg)\n![GitHub top language](https://img.shields.io/github/languages/top/RodolfoFerro/moltransform.svg)\n\n\nMolecular transformations for graphic displaying using Cartesian coordinates.\n\n## How to use it\n\n#### Generalities:\nThis package aims to transform `(x, y, z)` coordinates of molecules by reading and writing directly from a `.xyz` file and specifying the transformation vector. For each transformation function in the `transform` module, a `verbose` flag can be set `True` to print the transformation matrix to be applied for all `(x, y, z)` coordinates.\n\n### Opening a file\n\nTo load a file, we will use the `read_xyz` function by passing to it the path to the corresponding file to be opened.\n\nAn example on how to load a `.xyz` file:\n```bash\n>>> from moltransform.io import read_xyz\n>>> positions_matrix = read_xyz("path/to/file.xyz")\n```\n\n### Centering coordinates\n\nCenter the molecules\' coordinates by finding the center position of all `(x, y, z)` coordinates.\n```bash\n>>> from moltransform.transform import center\n>>> centered_positions = center(positions_matrix)\n```\n\n### Translating coordinates\n\nTranslate a molecule using a specific vector `(a, b, c)`. This implies:\n<center>\n\t<img src="https://latex.codecogs.com/svg.latex?\\fn_cm&space;\\hspace*{-18}&space;x&space;\\rightarrow&space;x&space;&plus;&space;a,\\newline&space;y&space;\\rightarrow&space;y&space;&plus;&space;b,\\newline&space;z&space;\\rightarrow&space;z&space;&plus;&space;c" title="\\hspace*{-18} x \\rightarrow x + a,\\newline y \\rightarrow y + b,\\newline z \\rightarrow z + c" />\n</center>\n\n```bash\n>>> from moltransform.transform import translate\n>>> translated_positions = translate(positions_matrix, [a, b, c])\n```\n\n\n### Scaling coordinates\n\nScale the molecule along the 3-axis by a vector `(a, b, c)`. This implies:\n<center>\n\t<img src="https://latex.codecogs.com/svg.latex?\\fn_cm&space;\\hspace*{-18}&space;x&space;\\rightarrow&space;ax,\\newline&space;y&space;\\rightarrow&space;by,\\newline&space;z&space;\\rightarrow&space;cz" title="\\hspace*{-18} x \\rightarrow ax,\\newline y \\rightarrow by,\\newline z \\rightarrow cz" />\n</center>\n\n```bash\n>>> from moltransform.transform import scale\n>>> scaled_positions = scale(positions_matrix, [a, b, c])\n```\n\n### Saving into a file\n\nTo save transformed coordinates into a file, we will use the `write_xyz` function by passing to it the path to the corresponding file to be **created**.\n\nAn example on how to save into a `.xyz` file:\n```bash\n>>> from moltransform.io import write_xyz\n>>> write_xyz("path/to/file.xyz", positions_matrix)\n```',
    'author': 'Rodolfo Ferro',
    'author_email': 'rodolfoferroperez@gmail.com',
    'url': 'https://github.com/RodolfoFerro/moltransform',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
