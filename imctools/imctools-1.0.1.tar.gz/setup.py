# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['imctools',
 'imctools.external',
 'imctools.imagej',
 'imctools.io',
 'imctools.scripts']

package_data = \
{'': ['*']}

install_requires = \
['pandas', 'scikit-image>=0.14.3,<0.15.0', 'tifffile>=2019.6.18']

setup_kwargs = {
    'name': 'imctools',
    'version': '1.0.1',
    'description': 'Tools to handle IMC data',
    'long_description': "# imctools\n\n[![Build Status](https://travis-ci.org/BodenmillerGroup/imctools.svg?branch=master)](https://travis-ci.org/BodenmillerGroup/imctools)\n[![Documentation Status](https://readthedocs.org/projects/imctools/badge/?version=latest)](https://imctools.readthedocs.io/en/latest/?badge=latest)\n\nAn IMC file conversion tool that aims to convert IMC rawfiles (.mcd, .txt) into an intermediary ome.tiff, containing all the relevant metadata. Further it contains tools to generate simpler tiff files that can be directly be used as input files for e.g. CellProfiller, Ilastik, Fiji etc.\n\nFurther imctools can directly work as a FIJI plugin, exploiting the Jython language. That allows that IMC data can be directly visualized in FIJI.\n\nFor a description of the associated segmentation pipline, please visit: https://github.com/BodenmillerGroup/ImcSegmentationPipeline\n\nDocumentation: https://imctools.readthedocs.io\n\n## Features\n\n- MCD lazy data access using memorymaps\n- Full MCD metadata access\n- TXT file loading\n- OME-TIFF loading\n- OME-TIFF/TIFF export (including optional compression)\n\n## Prerequisites\n\n- The package is written for Python3, but should also work with Python2\n- The core functions have a 'base' pure Python/Jython implementation with no dependencies outside the standard libraries.\n- The fast functions do need Python packages, such as numpy, scipy etc. installed.\n\n## Installation\n\nUse the pip installation manger to directly install the package from Github:\n\n```\npip install git+https://github.com/BodenmillerGroup/imctools.git\n```\n\n## Usage\n\nimctools is often used from jupyter as part of the preprocessing pipeline, mainly using the 'script' wrapper functions. Check 'notebooks/example_preprocessing_pipline.ipynb' as a template\n\nFurther imctools can be directly used as a module:\n\n```python\nimport imctools.io.mcdparser as mcdparser\nimport imctools.io.txtparser as txtparser\nimport imctools.io.ometiffparser as omeparser\nimport imctools.io.mcdxmlparser as meta\n\nfn_mcd = '/home/vitoz/Data/varia/201708_instrument_comp/mcd/20170815_imccomp_zoidberg_conc5_acm1.mcd'\n\nmcd = mcdparser.McdParser(fn_mcd)\n\n# parsed Metadata Access\nmcd.acquisition_ids\nmcd.get_acquisition_channels('1')\nmcd.get_acquisition_description('1')\n\n# a metadata object for comprehensive metadata access\nacmeta = mcd.meta.get_object(meta.ACQUISITION, '1')\nacmeta.properties\n\n# The common class to represent a single IMC acquisition is\n# The IMC acuqisition class.\n# All parser classes have a 'get_imc_acquisition' method\nimc_ac = mcd.get_imc_acquisition('1')\n\n# imc acquisitions can yield the image data\nimage_matrix = imc_ac.get_img_by_metal('Ir191')\n\n# or can be used to save the images using the image writer class\nfn_out ='/home/vitoz/temp/test.ome.tiff'\nimg = imc_ac.get_image_writer(filename=fn_out, metals=['Ir191', 'Yb172'])\nimg.save_image(mode='ome', compression=0, dtype=None, bigtiff=False)\n\n# as the mcd object is using lazy loading memory maps, it needs to be closed\n# or used with a context manager.\nmcd.close()\n```\n",
    'author': 'Vito Zanotelli',
    'author_email': 'vito.zanotelli@uzh.ch',
    'url': 'https://github.com/BodenmillerGroup/imctools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
