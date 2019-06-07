from mysql.toolkit import MySQL


# TODO: Remove prior to 1.5 release
class MySQLTools(MySQL):
    def __init__(self, config, enable_printing=True):
        """Wrapper class for MySQL"""
        super(MySQLTools, self).__init__(config, enable_printing)
