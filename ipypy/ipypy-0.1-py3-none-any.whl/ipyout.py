from copy import deepcopy
import json

from notebook.services.contents.filemanager import FileContentsManager


class IpypyManager(FileContentsManager):
    """
    ContentsManager that persists to a pure python file.
    """
    allow_hidden = False
    extension = '.nbdata'

    def guess_type(self, path, allow_directory=True):
        """
        Guess the type of a file.
        If allow_directory is False, don't consider the possibility that the
        file is a directory.
        """
        if path.endswith(self.extension):
            return 'notebook_data'
        if path.endswith('.ipynb'):
            return 'notebook'
        elif allow_directory and self.dir_exists(path):
            return 'directory'
        else:
            return 'file'

    def _get_outputs_uri(self, path):
        return path + self.extension

    def _split_model(self, model):
        shallow_model = deepcopy(model)
        outputs = {'type': 'file', 'format': 'text', 'content': {}}
        prefix = 'some-hash'
        for i, cell in enumerate(shallow_model['content']['cells']):
            if not cell.get('outputs', []):
                continue
            key = f'{prefix}-{i}'
            outputs['content'][key] = cell['outputs']
            cell['outputs'] = self._build_external_output(key)
        outputs['content'] = json.dumps(
            outputs['content'], sort_keys=True, indent=4)
        return shallow_model, outputs
    
    @staticmethod
    def _get_external_output_id(cell):
        if not cell['outputs']:
            return None
        out_0 = cell['outputs'][0]
        if out_0['output_type'] == 'external':
            return out_0.get('id')
        # if out_0['output_type'] == 'stream':
        #     return out_0.get('metadata', {}).get('external_id')
        return None

    @staticmethod
    def _build_external_output(key):
        return [
            {'output_type': 'external',
             'id': key
            }
            # {'output_type': 'stream', 'text': '',
            #  'metadata': {'external_id': key}
            # }
        ]

    def _merge_model(self, shallow_model, outputs_model):
        model = deepcopy(shallow_model)
        outputs = json.loads(outputs_model.get('content', '{}'))
        for cell in model['content']['cells']:
            key = self._get_external_output_id(cell)
            if key is None:
                continue
            cell['outputs'] = outputs.get(key, [])
        return model

    def save(self, model, path):
        """Save a file or directory model to path."""
        _type = self.guess_type(path)
        if _type != 'notebook':
            return super().save(model, path)
        else:
            shallow_model, outputs = self._split_model(model)
            super().save(outputs, self._get_outputs_uri(path))
            return super().save(shallow_model, path)

    def get(self, path, content=True, type=None, format=None):
        """Get a file or directory model."""
        result = super().get(path, content, type, format)
        if type is None:
            type = self.guess_type(path)
        elif type != 'notebook':
            return result
        # Now only handling notebooks
        if content:
            # look for the outputs file
            outputs_uri = self._get_outputs_uri(path)
            if self.file_exists(outputs_uri):
                outputs_data = super().get(outputs_uri, True, 'file')
                result = self._merge_model(result, outputs_data)
        
        return result

    def is_hidden(self, path):
        """Is path a hidden directory or file?"""
        if path.endswith(self.extension):
            return True
        return super().is_hidden(path)
