from onepanel.models import VolumeType
from onepanel.commands.volume_types import VolumeTypeViewController

class VolumeTypes():
    def __init__(self, conn):
        self.volume_type_view_controller = VolumeTypeViewController(conn)
    
    def list(self):
        vc = self.volume_type_view_controller
        items = vc.list(params='/volume_types')
        if items == None:
            print('No machine types found.')
            return

        vc.print_items(items, fields=['uid','name'], field_names=['UID','SPECS'])
        return [VolumeType.from_json(item) for item in items]