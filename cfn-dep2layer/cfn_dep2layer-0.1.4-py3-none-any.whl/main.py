import cfnyaml
import json
import os
import shutil
import tempfile
import platform
from dep2layer import downloaders

LAYER_PREFIX = 'Dep2layer'

def gettempfold():
  # In macOS, the default temporary directory cannot be shared with Docker VM.
  if platform.system() == 'Darwin':
    return tempfile.TemporaryDirectory(dir='/tmp')
  else:
    return tempfile.TemporaryDirectory()
  

def createlayer(template, layername, resource, downloader, cachedir):
  zippath = os.path.join(cachedir, '{}-{}.zip'.format(downloader.prefix, downloader.gethash()[:7]))
  if not os.path.isfile(zippath):
    print('Download dependencies...')
    with gettempfold() as tempdir:
      print('Using temp dir: {}'.format(tempdir))
      
      if not downloader.package(tempdir):
        print('Download faild.')
        return False
        
      with open(os.path.join(tempdir, '.dep2layer/hash.txt'), 'w') as f:
        f.write(downloader.gethash())
      
      shutil.make_archive(zippath[:-4], 'zip', tempdir)
      print('Created content zip: {}, length {}'.format(zippath, os.path.getsize(zippath)))
  else:
    print('Zip already exist: {}'.format(zippath))
    
  description = 'Create by dep2layer, contain packages: {}'.format('|'.join(downloader.getdeplist()))
  if len(description) > 256:
    description = description[:250] + '...'
  template['Resources'][layername] = {
      'Type': 'AWS::Serverless::LayerVersion',
      'Properties': {
        'LayerName': 'dep2layer-{}-{}'.format(downloader.prefix, downloader.gethash()[:7]),
        'Description': description,
        'ContentUri': zippath,
        'CompatibleRuntimes' : [resource['Properties']['Runtime']],
        'RetentionPolicy': 'Delete'
      }
  }
  
  return True


def work(templatepath, cachedir, outtemplatepath):
  
#  templatepath = os.path.abspath(DEFAULT_TEMPLATE if templatepath is None else templatepath)
  basedir = os.path.abspath(os.path.join(templatepath, '..'))
#  cachedir = os.path.abspath(os.path.join(basedir, DEFAULT_CACHE) if cachedir is None else cachedir)
#  outtemplatepath = os.path.abspath(os.path.join(basedir, DEFAULT_OUT_TEMPLATE) if outtemplatepath is None else outtemplatepath)
  
  try:
    with open(templatepath) as f:
      template = cfnyaml.load(f)
  except Exception as e:
    print('Error when load template file: {}\n{}'.format(templatepath, e))
    exit(1)
    
  try:
    os.makedirs(cachedir, exist_ok=True)
  except Exception as e:
    print('Error when create cache dir: {}\n{}'.format(cachedir, e))
    exit(1)
    
  for key, resource in list(template['Resources'].items()):
    if resource.get('Type') == 'AWS::Serverless::Function':
      runtime = resource['Properties']['Runtime']
      downloadercls = downloaders.cls.get(runtime)
      if downloadercls is None:
        continue
      downloader = downloadercls(resource, basedir)
      if not downloader.isdepfilesexists():
        print('Lambda [{}] with Runtime {} does not have dependency files'.format(key, runtime))
        continue
        
      print('Download dependencies for Lambda [{}] with Runtime {}'.format(key, runtime))
      
      layername = '{}{}H{}'.format(LAYER_PREFIX, downloader.prefix, downloader.gethash()[:7])
      if layername not in template:
        if not createlayer(template, layername, resource, downloader, cachedir):
          continue
          
      if 'Layers' not in resource['Properties']:
        resource['Properties']['Layers'] = []
      for ref in resource['Properties']['Layers']:
        if ref.logicalName.find(LAYER_PREFIX) == 0:
          ref.logicalName = layername
          break
      else:
        resource['Properties']['Layers'].append({'Ref': layername})

    
  try:
    with open(outtemplatepath, 'w') as f:
      if '.json' == outtemplatepath[-5:]:
        json.dump(template, f)
      else:
        f.write(cfnyaml.dump(template))
  except Exception as e:
    print('Error when create out template file: {}\n{}'.format(outtemplatepath, e))
    exit(1)
    
def clear():
  pass
