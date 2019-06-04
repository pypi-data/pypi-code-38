import os
import nbformat as nbf

from tornado import web
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from notebook.notebookapp import NotebookApp

base_path = os.path.dirname(__file__)
template_path = os.path.join(base_path, 'templates')
static_path = os.path.join(base_path, 'files', 'build')

ENDING = {
    "ipynb" : "notebooks"
}

class JupyterUploadHandler(IPythonHandler):
    @web.authenticated
    def get(self):
        # get the requested notebook
        prefix = os.getenv('UPLOAD_REDIRECT_PREFIX','')

        # get the url of the csv file
        URL = self.get_query_argument('url')

        # create new notebook
        nb = nbf.v4.new_notebook()

        code = \
"""\
import pandas as pd
import io
import requests
                        
csv_file_url = {0}
csv_file_contents = requests.get(csv_file_url).content
csv_file_df = pd.read_csv(io.StringIO(csv_file_contents.decode('utf-8'))) # csv file has been loaded into a pandas data frame                
"""

        nb['cells'] = [nbf.v4.new_code_cell(code.format('"' + URL + '"'))]
        fname = 'kubit.ipynb'

        with open(fname, 'w') as f:
            nbf.write(nb, f)

        self.redirect("%s/notebooks/%s" % (prefix, fname))


def _jupyter_server_extension_paths():
    return [
        {'module': 'kubit'}
    ]


def load_jupyter_server_extension(nb_server_app: NotebookApp):
    web_app = nb_server_app.web_app

    env = web_app.settings['jinja2_env']
    if hasattr(env.loader, 'loaders'):
        loaders = env.loader.loaders
    else:
        loaders = [env.loader]

    for loader in loaders:
        if hasattr(loader, 'searchpath'):
            loader.searchpath.append(template_path)
    web_app.settings['template_path'].append(template_path)

    web_app.settings['static_path'].append(static_path)

    base_url = web_app.settings.get('base_url', '/')
    handlers = [
        (url_path_join(base_url, '/upload'), JupyterUploadHandler,
         {})
    ]

    web_app.add_handlers('.*$', handlers)