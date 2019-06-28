from onepanel.models import Environment
from onepanel.commands.environments import EnvironmentViewController

class Environments():
    def __init__(self, conn):
        self.machine_type_view_controller = EnvironmentViewController(conn)
    
    def list(self):
        vc = self.machine_type_view_controller
        items = vc.list(params='/instance_templates')
        if items == None:
            print('No environments found.')
            return

        vc.print_items(items, fields=['uid','name'], field_names=['UID','ENVIRONMENT'])
        return [Environment.from_json(item) for item in items]