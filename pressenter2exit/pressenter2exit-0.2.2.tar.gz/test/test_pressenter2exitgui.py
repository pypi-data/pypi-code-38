
from time import time

from pressenter2exit import PressEnter2ExitGUI, __application_name__


def test_pressenter2exitgui():

    start_time = time()
    timeout = 5.0

    exit_control = PressEnter2ExitGUI(title=__application_name__, pre_message=f"press enter or wait for the program to timeout in {timeout} seconds:")

    # loops until return is pressed or we reach the end of our run time
    while exit_control.is_alive() and time() - start_time < timeout:
        exit_control.join(timeout)  # use join() instead of time.sleep() to ensure an immediate exit

    print()
    print(f'Exiting after {exit_control.get_duration()} seconds.')


if __name__ == "__main__":
    test_pressenter2exitgui()
