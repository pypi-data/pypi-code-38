import sys

if sys.version_info < (3,3):
    sys.exit('Sorry, Python < 3.3 is not supported')

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='jupyter-openbis-extension',
    version= '0.2.7',
    author='Swen Vermeul |  ID SIS | ETH Zürich',
    author_email='swen@ethz.ch',
    description='Extension for Jupyter notebooks to connect to openBIS and download/upload datasets, inluding the notebook itself',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://sissource.ethz.ch/sispub/jupyter-openbis-extension',
    packages=find_packages(),
    license='Apache Software License Version 2.0',
    install_requires=[
        'jupyter-nbextensions-configurator',
        'jupyter',
        'pybis>=1.8.4',
        'numpy',
        'tornado==5.1.1',
    ],
    python_requires=">=3.3",
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Programming Language :: JavaScript",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    data_files=[
        # like `jupyter nbextension install --sys-prefix`
        ("share/jupyter/nbextensions/jupyter-openbis-extension", [
            "jupyter-openbis-extension/static/connections.js",
            "jupyter-openbis-extension/static/downloadDialog.js",
            "jupyter-openbis-extension/static/connectionDialog.js",
            "jupyter-openbis-extension/static/uploadDialog.js",
            "jupyter-openbis-extension/static/spinner.gif",
            "jupyter-openbis-extension/static/entitySearcher.js",
            "jupyter-openbis-extension/static/main.js",
            "jupyter-openbis-extension/static/state.js",
            "jupyter-openbis-extension/static/common.js",
        ]),
        ("share/jupyter/nbextensions/jupyter-openbis-extension/jquery-select2/css", [
            "jupyter-openbis-extension/static/jquery-select2/css/select2.min.css",
            "jupyter-openbis-extension/static/jquery-select2/css/select2-bootstrap.css",
            "jupyter-openbis-extension/static/jquery-select2/css/select2-bootstrap.min.css",
            "jupyter-openbis-extension/static/jquery-select2/css/select2.css",
        ]),
        ("share/jupyter/nbextensions/jupyter-openbis-extension/jquery-select2/js", [
            "jupyter-openbis-extension/static/jquery-select2/js/select2.min.js",
            "jupyter-openbis-extension/static/jquery-select2/js/select2.full.min.js",
            "jupyter-openbis-extension/static/jquery-select2/js/select2.js",
            "jupyter-openbis-extension/static/jquery-select2/js/select2.full.js",
        ]),
        ("share/jupyter/nbextensions/jupyter-openbis-extension/jquery-select2/js/i18n", [
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/pt.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/vi.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/lv.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/gl.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/pl.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/el.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/et.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/is.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ko.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/hr.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ms.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/fi.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/th.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ru.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/eu.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/mk.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ja.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/he.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/bg.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/sr-Cyrl.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/id.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/az.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ca.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/nb.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/zh-CN.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/zh-TW.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/pt-BR.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/da.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/fa.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/de.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/en.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/sv.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/hi.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/uk.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/cs.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/km.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/fr.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/nl.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/sr.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/hu.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/lt.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ar.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/sk.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/it.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/es.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/ro.js",
            "jupyter-openbis-extension/static/jquery-select2/js/i18n/tr.js",
        ]),
        # like `jupyter nbextension enable --sys-prefix`
        ("etc/jupyter/nbconfig/notebook.d", [
            "jupyter-config/nbconfig/notebook.d/jupyter_openbis_extension.json"
        ]),
        # like `jupyter serverextension enable --sys-prefix`
        ("etc/jupyter/jupyter_notebook_config.d", [
            "jupyter-config/jupyter_notebook_config.d/jupyter_openbis_extension.json"
        ])
    ],
    zip_safe=False,
)
