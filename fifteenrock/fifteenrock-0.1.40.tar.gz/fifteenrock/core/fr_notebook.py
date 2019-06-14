from typing import *

from fifteenrock.core.core import deploy
from fifteenrock.lib import util, helper

# import nbformat
# import nbconvert
# from nbconvert import PythonExporter

# from notebook.notebookapp import list_running_servers
import re
from urllib.parse import urlencode, urljoin

import logging
import json
from urllib.request import urlopen
from os import path
# import ipykernel
import time

log = logging.getLogger(__name__)


# class StripMagicsProcessor(nbconvert.preprocessors.Preprocessor):
#     """
#     Preprocessor to convert notebooks to Python source while stripping
#     out all magics (i.e IPython specific syntax).
#     """
#
#     _magic_pattern = re.compile('^\s*(?P<magic>%%\w\w+)($|(\s+))')
#
#     def strip_magics(self, source):
#         """
#         Given the source of a cell, filter out all cell and line magics.
#         """
#         filtered = []
#         for line in source.splitlines():
#             match = self._magic_pattern.match(line)
#             if match is None:
#                 filtered.append(line)
#             else:
#                 msg = 'Stripping out IPython magic {magic} in code cell {cell}'
#                 message = msg.format(cell=self._cell_counter, magic=match.group('magic'))
#                 log.warn(message)
#         return '\n'.join(filtered)
#
#     def preprocess_cell(self, cell, resources, index):
#         if cell['cell_type'] == 'code':
#             self._cell_counter += 1
#             cell['source'] = self.strip_magics(cell['source'])
#         return cell, resources
#
#     def __call__(self, nb, resources):
#         self._cell_counter = 0
#         return self.preprocess(nb, resources)


# PREPROCESSORS = [StripMagicsProcessor()]


# OLD
# def notebook_file_name(ikernel):
#     """Return the full path of the jupyter notebook."""
#     # Check that we're running under notebook
#     if not (ikernel and ikernel.config['IPKernelApp']):
#         return
#
#     kernel_id = re.search('kernel-(.*).json',
#                           ipykernel.connect.get_connection_file()).group(1)
#     print('Kernel Id')
#     print(kernel_id)
#     servers = list_running_servers()
#     print('Running Servers')
#     print(servers)
#
#     for srv in servers:
#         query = {'token': srv.get('token', '')}
#         print('Query')
#         print(query)
#         print('Server Url')
#         print(srv['url'])
#         url = urljoin(srv['url'], 'api/sessions') + '?' + urlencode(query)
#         print("Url")
#         print(url)
#         for session in json.load(urlopen(url)):
#             if session['kernel']['id'] == kernel_id:
#                 relative_path = session['notebook']['path']
#                 return path.join(srv['notebook_dir'], relative_path)


def notebook_file_name(ikernel):
    """Return the full path of the jupyter notebook."""
    # Check that we're running under notebook
    if not (ikernel and ikernel.config['IPKernelApp']):
        return

    from notebook.notebookapp import list_running_servers
    import ipykernel

    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)

    servers = list_running_servers()
    for srv in servers:
        query = {'token': srv.get('token', '')}
        url = urljoin(srv['url'], 'api/sessions') + '?' + urlencode(query)
        for session in json.load(urlopen(url)):
            if session['kernel']['id'] == kernel_id:
                relative_path = session['notebook']['path']
                return path.join(srv['notebook_dir'], relative_path)


# def notebook_file_name(ikernel):
#     """Return the full path of the jupyter notebook."""
#     # Check that we're running under notebook
#     if not (ikernel and ikernel.config['IPKernelApp']):
#         return
#
#     kernel_id = re.search('kernel-(.*).json',
#                           ipykernel.connect.get_connection_file()).group(1)
#     print('Kernel')
#     print(kernel_id)
#
#     servers = list_running_servers()
#     print('Servers')
#     print(servers)
#
#     for srv in servers:
#         query = {'token': srv.get('token', '')}
#         print('Query')
#         print(query)
#         url = urljoin(srv['url'], 'api/sessions') + '?' + urlencode(query)
#         print('Url')
#         print(url)
#         for session in json.load(urlopen(url)):
#             if session['kernel']['id'] == kernel_id:
#                 relative_path = session['notebook']['path']
#                 return path.join(srv['notebook_dir'], relative_path)


def notebook_file_name_hub(ikernel, credentials):
    import requests
    import ipykernel
    import re
    from notebook.notebookapp import list_running_servers
    kernel_id = re.search('kernel-(.*).json', ipykernel.connect.get_connection_file()).group(1)
    token = credentials['hub_token']

    servers = list_running_servers()
    for srv in servers:
        base_url = srv['url']
        r = requests.get(
            url=base_url + 'api/sessions',
            headers={'Authorization': 'token {}'.format(token), })

        r.raise_for_status()
        sessions = r.json()
        for session in sessions:
            if session['kernel']['id'] == kernel_id:
                relative_path = session['notebook']['path']
                return path.join(srv['notebook_dir'], relative_path)


# def notebook_file_name_hub(ikernel, credentials):
#     import requests
#     import ipykernel
#     import re
#     from notebook.notebookapp import list_running_servers
#
#     token = credentials['hub_token']
#     print('Token')
#     print(token)
#
#     server = next(list_running_servers())
#     base_url = server['url']
#     r = requests.get(
#         url=base_url + 'api/sessions',
#         headers={'Authorization': 'token {}'.format(token), })
#
#     r.raise_for_status()
#     response = r.json()
#
#     kernel_id = re.search('kernel-(.*).json', ipykernel.connect.get_connection_file()).group(1)
#     relative_path = {r['kernel']['id']: r['notebook']['path'] for r in response}[kernel_id]
#     return relative_path


def deploy_notebook(project: str, function: str, requirements: List[str] = None, url: str = None,
                    dependencies: List = None,
                    credentials: Dict = None, credentials_file: str = None,
                    spec: Dict = None,
                    metadata: Dict = None) -> None:
    """
    This function should be only called from within a notebook. In all other scenarios, it is a no-op.
    :param project:
    :param function:
    :param requirements: List of pip libraries required by your code.
    :param url:
    :param dependencies:
    :param credentials:
    :param credentials_file:
    :param spec:
    :param metadata:
    :return:
    """

    if is_notebook():
        spec = spec or dict()
        metadata = metadata or dict()
        requirements = requirements or []
        save_current_notebook()
        credentials = helper.get_credentials(credentials, credentials_file)
        from IPython import get_ipython
        import ipykernel

        tmp_dir = util.tmp_folder()

        requirements_file = str(util.make_requirements_file_notebook(tmp_dir, requirements))

        try:
            module_path = tmp_dir / 'main.py'
            kernel = get_ipython()

            notebook_path = notebook_file_name_hub(kernel, credentials)

            convert_notebook(notebook_path, module_path)

            result = deploy(credentials=credentials, credentials_file=credentials_file,
                            project=project, function=function,
                            url=url,
                            main_file=str(module_path),
                            dependencies=dependencies,
                            requirements_file=requirements_file,
                            spec=spec,
                            metadata=metadata)
            print('Result:')
            print(result)
            return result
        except Exception as e:
            raise e
        finally:
            util.remove_dir(tmp_dir)
            pass

    else:
        pass


# def deploy_notebook_hub(project: str, function: str, url: str = None, dependencies: List = None,
#                     credentials: Dict = None, credentials_path: str = None) -> None:
#     if is_notebook():
#         save_current_notebook()
#         credentials = helper.get_credentials(credentials, credentials_path)
#         from IPython import get_ipython
#         import ipykernel
#
#         kernel = get_ipython()
#         print('Hi Rajiv')
#
#         notebook_path = notebook_file_name_hub(kernel, credentials)
#         print(notebook_path)
#
#
#
#     else:
#         print('WARNING: deploy_notebook is only executed from a notebook')
#         pass


def save_current_notebook():
    from IPython.display import Javascript

    script = '''
    require(["base/js/namespace"],function(Jupyter) {
        Jupyter.notebook.save_checkpoint();
    });
    '''
    Javascript(script)
    time.sleep(5)
    # print('This notebook has been saved.')


# def convert_notebook(notebook_path, module_path):
#     with open(notebook_path) as fh:
#         nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
#
#     exporter = PythonExporter()
#     source, meta = exporter.from_notebook_node(nb)
#
#     with open(module_path, 'w') as fh:
#         fh.writelines(source)


def convert_notebook(notebook_path, module_path, preprocessors=None):
    import nbconvert

    class StripMagicsProcessor(nbconvert.preprocessors.Preprocessor):
        """
        Preprocessor to convert notebooks to Python source while stripping
        out all magics (i.e IPython specific syntax).
        """

        _magic_pattern = re.compile('^\s*(?P<magic>%%\w\w+)($|(\s+))')

        def strip_magics(self, source):
            """
            Given the source of a cell, filter out all cell and line magics.
            """
            filtered = []
            for line in source.splitlines():
                match = self._magic_pattern.match(line)
                if match is None:
                    filtered.append(line)
                else:
                    msg = 'Stripping out IPython magic {magic} in code cell {cell}'
                    message = msg.format(cell=self._cell_counter, magic=match.group('magic'))
                    log.warn(message)
            return '\n'.join(filtered)

        def preprocess_cell(self, cell, resources, index):
            if cell['cell_type'] == 'code':
                self._cell_counter += 1
                cell['source'] = self.strip_magics(cell['source'])
            return cell, resources

        def __call__(self, nb, resources):
            self._cell_counter = 0
            return self.preprocess(nb, resources)

    class TerminalCommandsProcessor(nbconvert.preprocessors.Preprocessor):
        _terminal_pattern = re.compile('^!.*')

        def strip_terminal_commands(self, source):
            """
            Given the source of a cell, filter out all cell and line ter1minal commands.
            """
            filtered = []
            for line in source.splitlines():
                match = self._terminal_pattern.match(line)
                if match is None:
                    filtered.append(line)
                else:
                    msg = 'Commenting out IPython Terminal Commands {command} in code cell {cell}'
                    message = msg.format(cell=self._cell_counter, command=match.group(0))
                    log.warn(message)
                    filtered.append("#" + line)
            return '\n'.join(filtered)

        def preprocess_cell(self, cell, resources, index):
            if cell['cell_type'] == 'code':
                self._cell_counter += 1
                cell['source'] = self.strip_terminal_commands(cell['source'])
            return cell, resources

        def __call__(self, nb, resources):
            self._cell_counter = 0
            return self.preprocess(nb, resources)

    default_preprocessors = [StripMagicsProcessor(), TerminalCommandsProcessor()]
    preprocessors = preprocessors or default_preprocessors
    import nbformat
    from nbconvert import PythonExporter
    with open(notebook_path) as fh:
        nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)

    exporter = PythonExporter()
    for preprocessor in preprocessors:
        exporter.register_preprocessor(preprocessor)

    source, meta = exporter.from_notebook_node(nb)
    source = source.replace('get_ipython().run_line_magic', '')

    with open(module_path, 'w') as fh:
        fh.writelines(source)


def is_notebook():
    try:
        from IPython import get_ipython
    except ImportError as ex:
        return False

    try:
        kernel = get_ipython()
        shell = kernel.__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter
