import re
import json
import subprocess
from os.path import join, dirname, realpath 
from operator import itemgetter
from python_pachyderm import PfsClient, PpsClient
import python_pachyderm.client.pps.pps_pb2 as proto
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from importlib.util import spec_from_file_location, module_from_spec
from pachelm.utils import list_files, strToTimestamp, to_class_name 
from pachelm.migration import PachydermMigration

absolute_package_dir=dirname(realpath(__file__))

# Don't forget to adapt negative lookhead instead of hard code ^(?!.*bar).*$
EXTRACT_PATTERN = '(\d*)_(\d*)_(\d*)_(\d*)_(.*)_(pipeline|repo|seed)_([^.]*).(py|json)'

def extract_filename_to_migration(filename):
    matched = re.match(EXTRACT_PATTERN, filename)
    [year, month, day, time, resource, resource_type, migration, extension] = [ matched.group(i) for i in range(1, 9)  ]
    return {
      "time": strToTimestamp("%s_%s_%s_%s" % (year, month, day, time)),
      "resource": resource,
      "resource_type": resource_type,
      "migration": migration,
      "class_name": to_class_name(migration),
      "extension": extension,
      "path": filename
    }

# don't forget to sort .sort(key='time')
def from_dir_to_sorted_migrations(dirPath):
    files = list_files(dirPath)
    prepend_dir_path_to_migration = lambda m: { **m, 'path': '%s/%s' % (dirPath, m['path']) }
    migrations = map(extract_filename_to_migration, files)
    prepended_migrations = map(prepend_dir_path_to_migration, migrations)
    return list(prepended_migrations)

# loader=FileSystemLoader('pachelm', followlinks=True),
class PachydermAdminContext(object):
    'Singleton PachydermClient'
    def __init__(self, version, migrationsdir, pachydermconfigsdir, datadir):
        self.pfs = PfsClient()
        self.pps = PpsClient()
        self.version = version
        self.migrationsDir = migrationsdir
        self.migrations = from_dir_to_sorted_migrations(migrationsdir)
        self.pachydermConfigsDir = pachydermconfigsdir
        self.pachydermConfigs = from_dir_to_sorted_migrations(pachydermconfigsdir)
        self.dataDir = datadir
        self.env = Environment(
          loader=FileSystemLoader('%s/templates' % (absolute_package_dir), followlinks=True),
          autoescape=select_autoescape(['py', 'py.tmpl', 'tmpl', 'json.tmpl'])
        )

    def get_pipeline_path(self, baseFileName):
        return (join(self.migrationsDir, baseFileName) + ".py", join(self.pachydermConfigsDir, baseFileName) + ".json")

    def get_migrations_by_resource_type(self, reverse=False):
        def onlyType(resource_type):
            filtered = list(filter(lambda x : x['resource_type'] == resource_type, self.migrations))
            return sorted(filtered, key=itemgetter('time'), reverse=reverse)
        return (onlyType('repo'), onlyType('pipeline'), onlyType('seed'))

    def instantiate_module_from_migration(self, migration):
        spec = spec_from_file_location(migration['migration'], migration['path'])
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, migration['class_name'])(self)
    
    def find_pipeline_config(self, pipeline):
        filtered = list(filter(lambda config: config["resource"] == pipeline, self.pachydermConfigs))
        return filtered[0] if filtered else None

    def find_migration(self, migration):
        filtered = list(filter(lambda config: config["migration"] == migration, self.migrations))
        return filtered[0] if filtered else None

    def tear_up(self, migrations=None):
      self.__tear(migrations, 'up')

    def tear_down(self, migrations=None):
      self.__tear(migrations, 'down')

    def __tear(self, migrations, method):
      reverse = False if method == 'up' else True
      if not migrations:
        (repos, pipelines, seeds) = self.get_migrations_by_resource_type(reverse=reverse)
        migrations = (seeds + pipelines + repos) if reverse else (repos + pipelines + seeds)
      for migration in migrations:
        getattr(self.instantiate_module_from_migration(migration), "invoke_%s" % (method))()
