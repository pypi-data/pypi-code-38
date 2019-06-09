from action_base import action_base
from config_command import ConfigCommand
from config_command_item import ConfigCommandItem

class run_config_command(action_base):

    def run(self, command_item, buffer_name=''):
        cci = ConfigCommandItem()
        cci.command = command_item['name']
        cci.buffer_name = buffer_name
        ConfigCommand().run_config_command(cci)
