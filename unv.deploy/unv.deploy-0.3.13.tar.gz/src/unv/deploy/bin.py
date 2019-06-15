import os
import sys
import importlib

from pathlib import Path


def run():
    sys.path.append(str(Path().cwd()))
    name, commands = sys.argv[1], sys.argv[2:]
    module_path = None
    modules = ['app.settings.', 'secure.', '']
    for module in modules:
        module_path = f'{module}{name}'
        try:
            importlib.import_module(module_path)
            break
        except (ImportError, ModuleNotFoundError):
            continue
    if not module_path:
        raise ValueError(f'Settings "{name}" not found in modules {modules}')
    os.environ['SETTINGS'] = module_path

    from .tasks import DeployTasksManager
    manager = DeployTasksManager()
    manager.register_from_settings()
    manager.run(' '.join(commands))
