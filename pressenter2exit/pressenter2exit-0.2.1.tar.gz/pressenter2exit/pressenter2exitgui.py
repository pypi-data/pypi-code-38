
import time
import multiprocessing
import tkinter.messagebox
import tkinter


class PressEnter2ExitGUI(multiprocessing.Process):
    """
    Press Enter to Exit class.  Facilitates exit of a Python program in a controlled way.

    Supports programs that create processes.
    """
    def __init__(self, post_message: str = 'Exiting', pre_message: str = 'Exit?', title: str = None):
        """
        constructor

        :param post_message: message to be displayed after a enter hit (if None, no message is displayed).  Default is 'Enter pressed'.
        :param pre_message: message to be displayed via the input function (if None, input is silent).
        """
        super().__init__(daemon=True)
        self.post_message = post_message
        self.pre_message = pre_message
        self.title = title
        self.start_time = time.time()
        self.exit_time = None
        self.start()

    def run(self):
        """
        pop up a dialog box and return when the user has closed it
        """
        response = None
        root = tkinter.Tk()
        root.withdraw()
        while response is not True:
            response = tkinter.messagebox.askokcancel(title=self.title, message=self.pre_message)
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
