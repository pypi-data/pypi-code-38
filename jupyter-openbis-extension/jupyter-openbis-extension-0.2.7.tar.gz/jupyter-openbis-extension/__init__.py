name = 'jupyter-openbis-extension.server'
__author__ = 'Swen Vermeul'
__email__ = 'swen@ethz.ch'
__version__ = '0.2.7'

def _jupyter_server_extension_paths():
    return [{
        "module": "jupyter-openbis-extension.server"
    }]

# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [{
        'name': 'jupyter-openbis-extension',
        'label': 'Jupyter openBIS extension',
        'section': "notebook",
    #    # the path relative to the `jupyter-openbis-extension` directory containing the JavaScript
        'src': "static",
    #    # directory in the `nbextension/` namespace
        'dest': "openbis",
        # _also_ in the `nbextension/` namespace
        'require' : "openbis/main"
    }]

def load_jupyter_server_extension(nbapp):
    nbapp.log.info("jupyter-openbis-extension module enabled!")
