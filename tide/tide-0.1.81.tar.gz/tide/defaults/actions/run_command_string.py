from config import Config
from action_base import action_base
from command_handler import CommandHandler

class run_command_string(action_base):

    def run(self, command_item, buffer_name=''):
        variable_name = command_item['variable_name']
        variable_value = Config().get()["variables"].get(variable_name, None)
        if variable_value:
            return CommandHandler().run_command(variable_value, buffer_name)
