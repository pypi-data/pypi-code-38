from events import Events


class RemoteControlEvents(Events):
    __events__ = ('on_any',
                  'on_north', 'on_east', 'on_south', 'on_west',
                  'on_select', 'on_start',
                  'on_cross_north_p', 'on_cross_north_r', 'on_cross_south_p', 'on_cross_south_r',
                  'on_cross_west_p', 'on_cross_west_r', 'on_cross_east_p', 'on_cross_east_r',
                  'on_trigger_left', 'on_trigger_right',
                  'on_shoulder_left_p', 'on_shoulder_left_r', 'on_shoulder_right_p', 'on_shoulder_right_r',
                  'on_stick_left_north', 'on_stick_left_south', 'on_stick_left_east', 'on_stick_left_west',
                  'on_stick_right_north', 'on_stick_right_south', 'on_stick_right_east', 'on_stick_right_west',
                  'on_stick_left_y', 'on_stick_left_x', 'on_stick_left', 'on_stick_right_y', 'on_stick_right_x',
                  'on_stick_right', 'wake_up')
