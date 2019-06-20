from action_base import action_base
import interpolate as Interpolate

class print_debug(action_base):

    def run(self, command_item, buffer_name=''):
        msg = command_item.get("msg", '')
        interpolated_message = Interpolate.interpolate_variables(msg)
        print_buffer_name = command_item.get("buffer_name", 0)
        if print_buffer_name:
            print("print_debug - buffer name: " + buffer_name)
        print("print_debug - " + str(interpolated_message))
