# structure.py - Routines for generation app structure
import os
import stat
from jinja2 import Environment, Template, TemplateError, UndefinedError, TemplateNotFound, FileSystemLoader
from smoacks.sconfig import sconfig

class SmoacksStructure:
    def __init__(self):
        self.name = 'SmoacksStructure'
        self.env = [
            {'template': 'api_util.jinja',
             'dir': sconfig['structure']['utildir'],
             'outfile': "api_util.py",
             'module_dir': True},
            {'template': 'app-env.jinja',
             'dir': sconfig['structure']['bindir'],
             'outfile': "app-env"},
            {'template': 'base.jinja',
             'dir': os.path.join(sconfig['structure']['datamodeldir'],
                                 sconfig['structure']['gensubdir']),
             'outfile': 'base.py',
             'module_dir': True},
            {'template': 'dev-api-server.jinja',
             'dir': sconfig['structure']['kubedir'],
             'outfile': "dev-api-server.yaml"},
            {'template': 'Dockerfile.jinja',
             'outfile': "Dockerfile"},
            {'template': 'gitignore.jinja',
             'outfile': ".gitignore",
             'overwrite': False},
            {'template': 'local-env.jinja',
             'dir': sconfig['structure']['bindir'],
             'outfile': "local-env"},
            {'template': 'schema.jinja',
             'dir': sconfig['structure']['specdir'],
             'outfile': sconfig['parameters']['source_spec'],
             'overwrite': False},
            {'template': 'server-loop.jinja',
             'dir': sconfig['structure']['sourcedir'],
             'outfile': "server-loop",
             'executable': True},
            {'template': 'server_logging.jinja',
             'dir': sconfig['structure']['sourcedir'],
             'outfile': "server_logging.yaml"},
            {'template': 'server.jinja',
             'dir': sconfig['structure']['sourcedir'],
             'outfile': "server.py"},
            {'template': 'shutdown.jinja',
             'dir': sconfig['structure']['apiobjectdir'],
             'outfile': "shutdown.py",
             'module_dir': True},
            {'template': 'test-api-server.jinja',
             'dir': sconfig['structure']['kubedir'],
             'outfile': "test-api-server.yaml"},
            {'template': 'testme.jinja',
             'dir': sconfig['structure']['bindir'],
             'outfile': 'testme',
             'executable': True},
            {'template': 'TestUtil.jinja',
             'dir': sconfig['structure']['testdir'],
             'outfile': 'TestUtil.py',
             'module_dir': True}
        ]
        self.template_dict = sconfig['env_defaults']
        self.template_dict['smoacks_local_dev_path'] = os.path.join(sconfig['structure']['pvPathRoot'],
                                                                    sconfig['env_defaults']['smoacks_app_name'])

    def renderEnvironment(self):
        env = Environment(
            loader = FileSystemLoader('templates')
        )
        # Ensure there is a coverage directory with a runType.bash in it
        if not os.path.isdir('coverage'):
              coverpath = os.path.join(sconfig['structure']['root'], 'coverage')
              os.makedirs(coverpath, exist_ok=True)
              rtfile = open(os.path.join(coverpath, 'runType.bash'), "w")
              rtfile.write('export run_coverage=0')
              rtfile.close()
        for filespec in self.env:
           template = env.get_template(filespec['template'])
           filedir = os.path.join(sconfig['structure']['root'], filespec['dir']) if 'dir' in filespec and filespec['dir'] else sconfig['structure']['root']
           if not os.path.isdir(filedir):
              os.makedirs(filedir, exist_ok=True)
              if 'module_dir' in filespec and filespec['module_dir']:
                  tmf_file = open(os.path.join(filedir, '__init__.py'), "w")
                  tmf_file.close()
           outfilename = os.path.join(filedir, filespec['outfile'])
           if not os.path.isfile(outfilename) or 'overwrite' not in filespec or filespec['overwrite']:
               outfile = open(outfilename, "w")
               try:
                   filestring = template.render(self.template_dict)
                   outfile.write(filestring)
                   if 'executable' in filespec and filespec['executable']:
                       perm = os.stat(os.path.join(filedir, filespec['outfile']))
                       os.chmod(os.path.join(filedir, filespec['outfile']), perm.st_mode | stat.S_IEXEC)
                   outfile.close() 
               except TemplateNotFound:
                   print('Caught a TemplateNotFoundError on {}'.format(filespec['template']))
               except UndefinedError:
                   print('Caught a UndefinedError on {}'.format(filespec['template']))
               except TemplateError:
                   print('Caught a TemplateError on {}'.format(filespec['template']))
               except:
                   print('Caught an untyped error on {}'.format(filespec['template']))
           else:
               print('Skipping {} because it exists and should not be overwritten'.format(filespec['outfile']))
