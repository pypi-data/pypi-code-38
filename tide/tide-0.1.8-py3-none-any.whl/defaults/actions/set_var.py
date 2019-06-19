from config import Config
from action_base import action_base
import interpolate as Interpolate

class set_var(action_base):

    def run(self, command_item, buffer_name=''):
        name = command_item.get("name", '')
        if name:
            value = command_item.get("value", '')
            Config().get()["variables"][name] = Interpolate.interpolate_variables(value)
