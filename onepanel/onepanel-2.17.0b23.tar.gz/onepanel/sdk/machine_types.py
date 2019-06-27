from onepanel.models import MachineType
from onepanel.commands.machine_types import MachineTypesViewController

class MachineTypes():
    def __init__(self, conn):
        self.machine_type_view_controller = MachineTypesViewController(conn)
    
    def list(self):
        vc = self.machine_type_view_controller
        items = vc.list(params='/machine_types')
        if items == None:
            print('No machine types found.')
            return

        vc.print_items(items, fields=['uid','name'], field_names=['UID','SPECS'])
        return [MachineType.from_json(item) for item in items]