'''
`module layout`
```
automation/
  __init__.py
  __assets__/
    installer/
      nginx.conf.j2
  installer.py
```

`installer.py`
```
from lura import assets
from lura.run import run
from lura.plates import jinja2

class Install:

  def install(self):
    run('apt-get install -y nginx')
    conf_tmpl_path = assets.path(self, 'nginx.conf.j2')
    env = {'server_name': 'www.funhub.com'}
    jinja2.expandff(env, conf_tmpl_path, '/etc/nginx/sites-enabled/funhub.com')
    run('systemctl reload nginx')
```
'''

import os
import inspect
import types
from importlib import import_module
from lura import logs, plates

log = logs.get_logger(__name__)

def resolve(module):
  'Return the absolute path to the assets directory for a module.'

  if not hasattr(module, '__file__'):
    log.noise(f'resolve({module}) __file__ missing')
    return None
  mod_dir = os.path.dirname(module.__file__)
  mod_name = module.__name__.split('.')[-1]
  log.noise(f'resolve({module}) __file__ -> {module.__file__}')
  log.noise(f'resolve({module}) __name__ -> {module.__name__}')
  log.noise(f'resolve({module}) mod_dir -> {mod_dir}')
  log.noise(f'resolve({module}) mod_name -> {mod_name}')
  assets_dir = os.path.join(mod_dir, path.asset_dir_name)
  mod_assets_dir = os.path.join(assets_dir, mod_name)
  log.noise(f'resolve({module}) -> {mod_assets_dir}')
  return mod_assets_dir

def lookup(obj, name):
  assets_dir = path.resolve(import_module(obj.__module__))
  if not assets_dir:
    log.noise(f'lookup({obj}, {name}) __module__ -> None')
    return None
  log.noise(f'lookup({obj}, {name}) __module__ -> {obj.__module__}')
  asset = assets_dir
  if name:
    asset = os.path.join(assets_dir, name)
  if os.path.exists(asset) or os.path.islink(asset):
    log.noise(f'lookup({obj}, {name}) FOUND -> {asset}')
    return asset
  log.noise(f'lookup({obj}, {name}) MISSING -> {asset}')
  return None

def path(obj, name=None, bases=True):
  '''
  Return the absolute path for an asset. `obj` is resolved to a module, and the
  module is passed to `resolve()`. `name` is looked up within the module's
  assets directory.

  `obj` - function or class type
  `name` - file path relative to the `obj`'s module assets directory
  '''
  result = None
  if isinstance(obj, types.FunctionType):
    result = path.lookup(obj, name)
  elif inspect.isclass(obj):
    for cls in inspect.getmro(obj):
      asset = path.lookup(cls, name)
      if asset:
        result = asset
        break
  else:
    return path(type(obj), name, bases)
  if result:
    log.noise(f'path({obj}, name={name}, bases={bases}) FOUND -> {result}')
    return result
  log.noise(f'path({obj}, name={name}, bases={bases}) -> MISSING')
  raise FileNotFoundError(f"Asset '{name}' not found for obj {obj}")

path.asset_dir_name = '__assets__'
path.lookup = lookup
path.resolve = resolve

def open(obj, name, mode, encoding=None):
  log.noise(f'open({obj}, {mode}, encoding={encoding})')
  return open(path(obj, name), mode=mode, encoding=encoding)

def slurp(obj, name, mode, encoding=None):
  log.noise(f'slurp({obj}, {name}, {mode}, encoding={encoding})')
  with open(path(obj, name), mode=mode, encoding=encoding) as fd:
    return fd.read()

def loadf(obj, name, encoding=None):
  log.noise(f'loadf({obj}, {name}, encoding={encoding}')
  return formats.loadf(path(obj, name), encoding=encoding)
