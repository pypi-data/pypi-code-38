
from time import time

from pressenter2exit import PressEnter2Exit


def test_pressenter2exit():

    # Pass -s to pytest if you get:
    #   OSError: reading from stdin while output is captured
    # This will cause the pytest run to ignore user input and use the "time out" feature, but it will at least run.
    # It is better to run run_test.bat and test pressenter2exit manually.

    start_time = time()
    timeout = 5.0

    exit_control = PressEnter2Exit(pre_message=f"press enter or wait for the program to timeout in {timeout} seconds:")

    # loops until return is pressed or we reach the end of our run time
    while exit_control.is_alive() and time() - start_time < timeout:
        exit_control.join(timeout)  # use join() instead of time.sleep() to ensure an immediate exit

    print()
    print(f'Exiting after {exit_control.get_duration()} seconds.')


if __name__ == "__main__":
    test_pressenter2exit()
