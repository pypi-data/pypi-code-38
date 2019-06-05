
import time
import threading


class PressEnter2Exit(threading.Thread):
    """
    Press Enter to Exit class.  Facilitates exit of a Python CLI program in a controlled way.

    Do *NOT* use this class if your program creates processes.  Use PressEnter2ExitGUI instead.

    """
    def __init__(self, post_message: str = 'Enter pressed', pre_message: str = 'Press enter to exit:'):
        """
        constructor

        :param post_message: message to be displayed after a enter hit (if None, no message is displayed).  Default is 'Enter pressed'.
        :param pre_message: message to be displayed via the input function (if None, input is silent).
        """
        super().__init__(daemon=True)
        self.post_message = post_message
        self.pre_message = pre_message
        self.start_time = time.time()
        self.exit_time = None
        self.start()

    def run(self):
        """
        run method
        """
        if self.pre_message is None:
            try:
                input()  # pre message of None causes the input to be silent
            except EOFError:
                pass
        else:
            try:
                input(self.pre_message)
            except EOFError:
                pass
        if self.post_message:
            print(self.post_message)
        self.exit_time = time.time()

    def get_start_time(self) -> float:
        """
        get time of instantiation (in seconds since epoch)

        :return: time of instantiation (in seconds since epoch)
        """
        return self.start_time

    def get_enter_duration(self) -> (float, None):
        """
        time from instantiation to when enter was pressed

        :return: time from instantiation to when enter was pressed or None if enter not yet pressed (in seconds)
        """
        if self.exit_time is None:
            return None
        return self.exit_time - self.start_time

    def get_duration(self) -> float:
        """
        time since instantiation

        :return: time since instantiation (in seconds)
        """
        return time.time() - self.start_time

    def get_reaction_time(self) -> float:
        """
        get how long it took the program that uses this class to react to the pressing of enter

        :return: the time from when enter was pressed to now (in seconds)
        """
        if self.exit_time is None:
            # enter was never hit, so our reaction time is zero
            return 0.0
        return time.time() - self.exit_time
