import click
from onepanel.models.dataset_mount import DatasetMount

class DatasetMountIdentifierParamType(click.ParamType):
    name = 'dataset mount'

    def convert(self, value, param, ctx):
        """Accepts multiple key/value pairs separated by commas. The key/value is separated by equals sign.
           Order of the parameters doesn't matter.
           
           For example: source=andreyonepanel/images,version=3,destination=cats

           Source is required.
           Destination is optional. Defaults to None.
           Version is optional. Defaults to None, which indicates "use the latest".
        """
        try:
            identifier = DatasetMount()
            key_values = value.split(',')
            map = {}

            for key_value in key_values:
                parts = key_value.split('=')
                map[parts[0]] = parts[1]

            identifier.set_source(map['source'])
            identifier.set_version(map['version'])
            identifier.destination = map['destination']

            return identifier
        except ValueError:
            self.fail('%s is not a valid dataset mount' % value, param, ctx)

DATASET_MOUNT_IDENTIFIER = DatasetMountIdentifierParamType()