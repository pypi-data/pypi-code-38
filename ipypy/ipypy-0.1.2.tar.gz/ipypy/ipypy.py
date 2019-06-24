from copy import deepcopy
from itertools import repeat
import json

from notebook.services.contents.filemanager import FileContentsManager


class SplitManager(FileContentsManager):
    """
    ContentsManager that persists data splitted
    """
    allow_hidden = False

    def guess_type(self, path, allow_directory=True):
        """
        Guess the type of a file.
        If allow_directory is False, don't consider the possibility that the
        file is a directory.
        """
        if path.endswith('.ipynb'):
            return 'notebook'
        elif allow_directory and self.dir_exists(path):
            return 'directory'
        else:
            return 'file'

    def _get_splitted_uri(self, path):
        return path.replace('.ipynb', self.extension)

    def save(self, model, path):
        """Save a file or directory model to path."""
        _type = self.guess_type(path)
        if _type != 'notebook':
            return super().save(model, path)
        else:
            shallow_model, splitted = self._split_model(model)
            super().save(splitted, self._get_splitted_uri(path))
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
            # look for the splitted file
            splitted_uri = self._get_splitted_uri(path)
            if self.file_exists(splitted_uri):
                splitted_data = super().get(splitted_uri, True, 'file')
                result = self._merge_model(result, splitted_data)
        
        return result

    def is_hidden(self, path):
        """Is path a hidden directory or file?"""
        if path.endswith(self.extension):
            return True
        return super().is_hidden(path)


class SplitCodeManager(SplitManager):
    """
    ContentsManager that persists code to a pure code file.
    """
    extension = '.ipypy'
    comment_prefix = '# <cell-init>'

    @classmethod
    def _comment(cls, key):
        # Hardcoded python comment
        return f'{cls.comment_prefix} cell-id: {key}'

    def _split_model(self, model):
        shallow_model = deepcopy(model)
        splitted = {'type': 'file', 'format': 'text', 'content': {}}
        prefix = 'some-hash'
        for i, cell in enumerate(shallow_model['content']['cells']):
            if not cell['cell_type'] == 'code':
                continue
            key = f'{prefix}-{i}'
            splitted['content'][key] = cell['source']
            self._format_cell_after_split(cell, key)
        
        # lets format the file now
        code_lines = []
        for k, value in splitted['content'].items():
            code_lines.append(self._comment(k))
            if isinstance(value, (list, tuple)):
                code_lines.extend(value)
            else:
                code_lines.append(value)
        splitted['content'] = '\n'.join(code_lines)
        return shallow_model, splitted

    @staticmethod
    def _format_cell_after_split(cell, key):
        cell['source'] = ''
        cell['metadata']['code_id'] = key

    @staticmethod
    def _get_split_key(cell):
        if not cell['cell_type'] == 'code':
            return None
        return cell.get('metadata', {}).get('code_id')

    def _parse_source_data(self, data):
        chunks = data.get('content', '').split(self.comment_prefix)
        code = {}
        detached_code = []  # someone inserted new cells directly in code file
        for chunk in chunks:
            if not chunk:
                continue
            head, *lines = chunk.splitlines(keepends=True)
            if ':' in head:
                key = head.split(':')[1].strip()
            else:
                key = None
            if lines:
                last_line = lines[-1]
                if last_line.endswith('\n'):  # there is always an extra newline added
                    lines[-1] = last_line[:-1]  # removed extra
            if key:
                code[key] = lines
            else:
                detached_code.append(lines)
        return code, detached_code

    def _merge_model(self, shallow_model, splitted_model):
        model = deepcopy(shallow_model)
        code, detached_code = self._parse_source_data(splitted_model)

        for cell in model['content']['cells']:
            key = self._get_split_key(cell)
            if key is None or key not in code:
                continue
            cell['source'] = code.pop(key)
        new_cells = list(code.items())  # unused source lines
        new_cells += zip(repeat(None), detached_code)
        for extra_key, source_lines in new_cells:
            model['content']['cells'].append(
                { "cell_type" : "code",
                  "metadata" : {'code_id': extra_key},
                  "source" : source_lines,
                  "outputs": [],
                }
            )
        return model


class SplitOutputManager(FileContentsManager):
    """
    ContentsManager that persists output to a different file.
    """
    allow_hidden = False
    extension = '.nbout'

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
        return None

    @staticmethod
    def _build_external_output(key):
        return [
            {'output_type': 'external',
             'id': key
            }
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
