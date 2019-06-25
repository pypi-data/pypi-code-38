
import os
import dong.templates as templates
import dong.utils as utils

def define_structure(opts):
    s = {
        'setup.py': templates.make_template('setup_py', opts),
        opts['package']: {
            '__init__.py': templates.make_template('__init__', opts),
            'data': {
                '__init__.py': '',
                'default.py': templates.make_template('data', {**opts, **{'class_name': 'DefaultData'}}),
            },
            'model': {
                '__init__.py': '',
                'default.py': templates.make_template('model', {**opts, **{'class_name': 'DefaultModel'}}),
                'init': {
                    '__init__.py': '',
                    'default.py': templates.make_template('model/init', {**opts, **{'class_name': 'DefaultModelInit'}}),
                },
                'serializer': {
                    '__init__.py': '',
                    'default.py': templates.make_template('model/serializer', opts),
                },
                'train': {
                    '__init__.py': '',
                    'default.py': templates.make_template('model/train', opts),
                },
            },
            'config': {
                '__init__.py': '',
                'default.py': templates.make_template('config', opts),
            },
            'tune': {
                '__init__.py': '',
                'default.py': templates.make_template('tune', {**opts, **{'class_name': 'DefaultTune'}}),
            },
            'service': {
                '__init__.py': '',
                'default.py': templates.make_template('service', {**opts, **{'class_name': 'DefaultService'}}),
            },
        },
    }

    return s

def create_structure(struct, opts, prefix=None):
    if prefix is None:
        prefix = os.getcwd()

    changed = {}
    for name, content in struct.items():
        if isinstance(content, str):
            utils.create_file(os.path.join(prefix, name), content)
            changed[name] = content
        elif isinstance(content, dict):
            utils.create_directory(os.path.join(prefix, name))
            changed[name] = create_structure(struct[name], opts, prefix=os.path.join(prefix, name))
        elif content is None:
            pass

    return changed
