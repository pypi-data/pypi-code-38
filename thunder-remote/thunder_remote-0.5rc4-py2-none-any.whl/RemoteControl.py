import os
import csv

from multiprocessing import Process, Queue
from inputs import devices, get_gamepad
from RemoteControlEvents import RemoteControlEvents
from thunder_remote.ControllerMapping import ControllerMapping
from thunder_remote.DebugLevel import DebugLevel


class RemoteControl:

    event_queue = Queue()
    control_queue = Queue()

    def __init__(self, profile="default", debug_level=DebugLevel.NONE, profiles_path='profiles', start_sleeping=False):
        self.debug_level = debug_level
        self.is_sleeping = start_sleeping

        self.events = RemoteControlEvents()
        self.remote_online = False
        self.tries_loading_profile = 1
        self.profile = profile
        self.controller_name = "Unknown"
        self.thread = None
        self.remote_found = True
        self.profile_loaded = False
        self.profiles_path = profiles_path
        self.start_sleeping = start_sleeping
        self.alarm = None

        print "> INIT REMOTE CONTROL"
        print "> Looking for gamepad..."
        if not devices.gamepads:
            self.remote_found = False
            print "> No gamepad detected!"
        else:
            print "> Gamepad detected!"

        print ">"
        print "> Loading profile '" + self.profile + "'"

        controller_mapping = self.load_profile()
        if not self.profile_loaded:
            print "> Unable to load a profile!"
        else:
            print "> Profile for '" + self.controller_name + "' loaded!"

        print ">"

        if self.remote_found and self.profile_loaded:
            print "> Remote control is now ready for activation!"
            self.proc = Process(group=None, target=RemoteControl.control, name="thunder_remote",
                                args=(RemoteControl.event_queue, RemoteControl.control_queue, start_sleeping,
                                      debug_level, controller_mapping))

    def activate(self):
        if self.remote_online:
            print "> Remote control already activated!"
        else:
            self.remote_online = True
            if self.start_sleeping:
                self.sleep()

            print "> Remote control activated!"
            self.proc.start()

    def deactivate(self):
        self.remote_online = False
        RemoteControl.control_queue.put(["run", self.remote_online])
        print "> Remote control deactivated!"

    def wake(self):
        if self.is_sleeping:
            self.is_sleeping = False

            if self.debug_level == DebugLevel.BASIC:
                print "> [DEBUG] WAKE_UP"

    def sleep(self):
        if not self.is_sleeping:
            self.is_sleeping = True
            RemoteControl.control_queue.put(["sleep", self.is_sleeping])

            if self.debug_level == DebugLevel.BASIC:
                print "> [DEBUG] SLEEP"

    def listen(self):
        if not RemoteControl.event_queue.empty():
            action = RemoteControl.event_queue.get()

            code, state = None, None
            method = action[0]
            if len(action) == 3:
                code = action[1]
                state = action[2]

            for event in self.events.__iter__():
                if event.__name__ == method:
                    if code is not None and state is not None:
                        if self.debug_level == DebugLevel.QUEUE:
                            print "> [DEBUG] QUEUE-OUT: {0} {1}".format(code, state)

                        event.__call__(code, state)
                        return

                    event.__call__()

    def load_profile(self):
        controller_mapping = ControllerMapping()

        try:
            path = self.profiles_path + '/' + self.profile + '.csv'
            if self.debug_level == DebugLevel.BASIC:
                print ">", path

            if self.profiles_path is 'profiles':
                path = os.path.dirname(os.path.realpath(__file__)) + '/' + path

            if not os.path.isfile(path):
                print "> Profile '" + self.profile + "' not found!"
                return

            self.tries_loading_profile += 1
            with open(path, 'r') as csvFile:
                reader = csv.DictReader(csvFile)

                for profile in reader:
                    # CONTROLLER NAME
                    self.controller_name = profile['CONTROLLER']

                    # LEFT BUTTONS
                    controller_mapping.BTN_NORTH = profile['BTN_NORTH']
                    controller_mapping.BTN_EAST = profile['BTN_EAST']
                    controller_mapping.BTN_SOUTH = profile['BTN_SOUTH']
                    controller_mapping.BTN_WEST = profile['BTN_WEST']

                    # START AND SELECT
                    controller_mapping.START = profile['START']
                    controller_mapping.SELECT = profile['SELECT']

                    # CROSS
                    controller_mapping.CROSS_Y = profile['CROSS_Y']
                    controller_mapping.CROSS_X = profile['CROSS_X']

                    # STICK R & STICK L
                    controller_mapping.STICK_RIGHT_Y = profile['STICK_R_Y']
                    controller_mapping.STICK_RIGHT_X = profile['STICK_R_X']
                    controller_mapping.STICK_LEFT_Y = profile['STICK_L_Y']
                    controller_mapping.STICK_LEFT_X = profile['STICK_L_X']

                    # TRIGGER AND SHOULDER
                    controller_mapping.TRIGGER_R = profile['TRIGGER_R']
                    controller_mapping.SHOULDR_R = profile['SHOULDER_R']
                    controller_mapping.TRIGGER_L = profile['TRIGGER_L']
                    controller_mapping.SHOULDR_L = profile['SHOULDER_L']

                    # THUMBS
                    controller_mapping.THUMB_R = profile['THUMB_R']
                    controller_mapping.THUMB_L = profile['THUMB_L']

                    # WAKE UP
                    controller_mapping.WAKE_UP = profile['WAKE_UP']

                    # VALUES FOR STICK MOVEMENT
                    fward_vals = profile['FORWARD_VALUES'].split(';')
                    bward_vals = profile['BACKWARD_VALUES'].split(';')

                    controller_mapping.FORWARD_VALUES = range(int(fward_vals[0]), int(fward_vals[1]) + 1)
                    if fward_vals[2] == "True":
                        controller_mapping.FORWARD_VALUES.reverse()

                    controller_mapping.BACKWARD_VALUES = range(int(bward_vals[0]), int(bward_vals[1]) + 1)
                    if bward_vals[2] == "True":
                        controller_mapping.BACKWARD_VALUES.reverse()

                self.profile_loaded = True

        except (KeyError, IOError):
            print "> Invalid profile! Switching back to default!"
            self.profile = "default"
            if self.tries_loading_profile == 1:
                self.load_profile()
            else:
                self.profile_loaded = False

        return controller_mapping

    def is_available(self):
        return self.remote_found

    @classmethod
    def percent_value(cls, (state, common, alternate)):
        mod = 1
        values = common

        if state not in values:
            values = alternate
            mod = -1

            if state not in values:
                return 0

        return (state - float(values[0])) / (values[values.__len__() - 1] - values[0]) * mod

    @classmethod
    def control(cls, queue, c_queue, sleeping, debug, controller_mapping):
        is_running = True
        is_sleeping = sleeping
        debug_level = debug

        prev_cross_state = None

        while is_running:
            if not c_queue.empty():
                cmd = c_queue.get()
                if cmd[0] == "sleep":
                    is_sleeping = cmd[1]

                if cmd[0] == "run":
                    is_running = cmd[1]

            events = get_gamepad()
            for event in events:
                code = event.code
                state = event.state
                calc_props = (state, controller_mapping.FORWARD_VALUES, controller_mapping.BACKWARD_VALUES)

                if not is_sleeping:
                    if debug_level == DebugLevel.EVENT:
                        queue.put(["on_any", code, state])

                    # BUTTON RELEASED
                    if state == 0:

                        # RIGHT BUTTONS
                        if code in controller_mapping.BTN_NORTH:
                            queue.put(["on_north", code, state])

                        if code in controller_mapping.BTN_EAST:
                            queue.put(["on_east", code, state])

                        if code in controller_mapping.BTN_SOUTH:
                            queue.put(["on_south", code, state])

                        if code in controller_mapping.BTN_WEST:
                            queue.put(["on_west", code, state])

                        # START AND SELECT
                        if code in controller_mapping.START:
                            queue.put(["on_start", code, state])

                        if code in controller_mapping.SELECT:
                            queue.put(["on_select", code, state])

                    # CONTROLLER CROSS
                    if code in controller_mapping.CROSS_Y or code in controller_mapping.CROSS_X:

                        # CROSS NORTH AND SOUTH
                        if code in controller_mapping.CROSS_Y:
                            if state == -1:
                                queue.put(["on_cross_north_p", code, state])
                                prev_cross_state = -1

                            if state == 1:
                                queue.put(["on_cross_south_p", code, state])
                                prev_cross_state = 1

                            if state == 0:
                                if prev_cross_state == 1:
                                    queue.put(["on_cross_south_r", code, state])
                                else:
                                    queue.put(["on_cross_north_r", code, state])

                        # CROSS WEST AND EAST
                        if code in controller_mapping.CROSS_X:
                            if state == -1:
                                queue.put(["on_cross_west_p", code, state])
                                prev_cross_state = -1

                            if state == 1:
                                queue.put(["on_cross_east_p", code, state])
                                prev_cross_state = 1

                            if state == 0:
                                if prev_cross_state == 1:
                                    queue.put(["on_cross_east_r", code, state])
                                else:
                                    queue.put(["on_cross_west_r", code, state])

                    # TRIGGERS
                    if code in controller_mapping.TRIGGER_L or code in controller_mapping.TRIGGER_R:

                        # LEFT TRIGGER
                        if code in controller_mapping.TRIGGER_L:
                            queue.put(["on_trigger_left", code, state])

                        # RIGHT TRIGGER
                        if code in controller_mapping.TRIGGER_R:
                            queue.put(["on_trigger_right", code, state])

                    # SHOULDERS
                    if code in controller_mapping.SHOULDR_L or code in controller_mapping.SHOULDR_R:

                        # LEFT SHOULDER
                        if code in controller_mapping.SHOULDR_L:

                            # ON RELEASE
                            if state == 0:
                                queue.put(["on_shoulder_left_r", code, state])

                            # WHEN PRESSED
                            if state == 1:
                                queue.put(["on_shoulder_left_p", code, state])

                        # RIGHT SHOULDER
                        if code in controller_mapping.SHOULDR_R:

                            # ON RELEASE
                            if state == 0:
                                queue.put(["on_shoulder_right_r", code, state])

                            # WHEN PRESSED
                            if state == 1:
                                queue.put(["on_shoulder_right_p", code, state])

                    # LEFT STICK
                    if code in controller_mapping.STICK_LEFT_X or code in controller_mapping.STICK_LEFT_Y:

                        # ANY MOVEMENT
                        queue.put(["on_stick_left", code, RemoteControl.percent_value(calc_props)])

                        # X-AXIS
                        if code in controller_mapping.STICK_LEFT_X:

                            # ANY X-AXIS MOVEMENT
                            queue.put(["on_stick_left_x", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT EAST
                            if state in calc_props[1]:
                                queue.put(["on_stick_left_east", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT WEST
                            if state in calc_props[2]:
                                queue.put(["on_stick_left_west", code, RemoteControl.percent_value(calc_props)])

                        # Y-AXIS
                        if code in controller_mapping.STICK_LEFT_Y:

                            # ANY Y-AXIS MOVEMENT
                            queue.put(["on_stick_left_y", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT NORTH
                            if state in calc_props[1]:
                                queue.put(["on_stick_left_north", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT SOUTH
                            if state in calc_props[2]:
                                queue.put(["on_stick_left_south", code, RemoteControl.percent_value(calc_props)])

                    # RIGHT STICK
                    if code in controller_mapping.STICK_RIGHT_X or code in controller_mapping.STICK_RIGHT_Y:

                        # ANY MOVEMENT
                        queue.put(["on_stick_right", code, RemoteControl.percent_value(calc_props)])

                        # X-AXIS
                        if code in controller_mapping.STICK_RIGHT_X:

                            # ANY X-AXIS MOVEMENT
                            queue.put(["on_stick_right_x", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT EAST
                            if state in calc_props[1]:
                                queue.put(["on_stick_right_east", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT WEST
                            if state in calc_props[2]:
                                queue.put(["on_stick_right_west", code, RemoteControl.percent_value(calc_props)])

                        # Y-AXIS
                        if code in controller_mapping.STICK_RIGHT_Y:

                            # ANY Y-AXIS MOVEMENT
                            queue.put(["on_stick_right_y", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT NORTH
                            if state in calc_props[1]:
                                queue.put(["on_stick_right_north", code, RemoteControl.percent_value(calc_props)])

                            # MOVEMENT SOUTH
                            if state in calc_props[2]:
                                queue.put(["on_stick_right_south", code, RemoteControl.percent_value(calc_props)])
                else:
                    if code in controller_mapping.WAKE_UP:
                        is_sleeping = False
                        queue.put(['wake_up'])
