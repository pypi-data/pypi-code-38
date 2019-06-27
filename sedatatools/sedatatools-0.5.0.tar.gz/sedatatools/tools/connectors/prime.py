import configparser
from sys import platform


class Prime:
    def __init__(self):
        if platform == 'linux':
            self.secrets_path = '/home/vedad/prime_secrets'
        elif platform == 'win32':
            self.secrets_path = r'C:\Users\Datasoft\prime_secrets'
        else:
            self.secrets_path = ''

        self.config = configparser.ConfigParser()
        self.config.read(self.secrets_path)
        self.user_name = self.config.get("prime", "user_name")
        self.password = self.config.get("prime", "password")

    def __repr__(self):
        return f'Username: {self.user_name}, password: {self.password}'
