from datahelper.mssql.mssql_data_helper import MSSQLDataHelper
from datahelper.mssql.go_server_production import select as Selector

class DataHelper(MSSQLDataHelper):

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='GoServer_Production_ReadOnly'):
        super().__init__( 
            logger=logger,
            config_file=config_file,
            host_name=host_name)

    def connect(self):
        super().connect()

    def get_vm_list(self):
        return super().get_data(Selector.get_vm_list)
        