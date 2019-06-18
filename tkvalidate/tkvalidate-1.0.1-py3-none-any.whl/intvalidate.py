import tkinter as tk


def int_validate(entry_widget, from_=None, to=None):
    """
    Validates an entry_widget so that only integers within a specified range may be entered

    :param entry_widget: The tkinter.Entry widget to validate
    :param from_: The start limit of the integer
    :param to: The end limit of the integer

    :return:       None
    """
    from_ = from_ if from_ is not None else entry_widget.configure()['from'][4]
    to = to if to is not None else entry_widget.configure()['to'][4]
    num_str = entry_widget.get()
    current = None if (not _is_int(num_str)) else int(num_str)
    check = _NumberCheck(entry_widget, from_, to, current=current)
    entry_widget.config(validate='all')
    entry_widget.config(validatecommand=check.vcmd)
    entry_widget.bind('<FocusOut>', lambda event: _validate(entry_widget, check))
    _validate(entry_widget, check)


def _is_int(num_str):
    """
    Returns whether or not a given string is an integer

    :param num_str: The string to test

    :return: Whether or not the string is an integer
    """
    try:
        int(num_str)
        return True
    except ValueError:
        return False


def _validate(entry, num_check):
    """
    Validates an entry so if there is invalid text in it it will be replaced by the last valid text

    :param entry: The entry widget
    :param num_check: The _NumberCheck instance that keeps track of the last valid number

    :return:    None
    """
    if not _is_int(entry.get()):
        entry.delete(0, tk.END)
        entry.insert(0, str(num_check.last_valid))


class _NumberCheck:
    """
    Class used for validating entry widgets, self.vcmd is provided as the validatecommand
    """

    def __init__(self, parent, min_, max_, current):
        self.parent = parent
        self.low = min_
        self.high = max_
        self.vcmd = parent.register(self.in_integer_range), '%d', '%P'

        if _NumberCheck.in_range(0, min_, max_):
            self.last_valid = 0
        else:
            self.last_valid = min_
        if current is not None:
            self.last_valid = current

    def in_integer_range(self, type_, after_text):
        """
        Validates an entry to make sure the correct text is being inputted
        :param type_:        0 for deletion, 1 for insertion, -1 for focus in
        :param after_text:   The text that the entry will display if validated
        :return:
        """

        if type_ == '-1':
            if _is_int(after_text):
                self.last_valid = int(after_text)

        # Delete Action, always okay, if valid number save it
        elif type_ == '0':
            try:
                num = int(after_text)
                self.last_valid = num
            except ValueError:
                pass
            return True

        # Insert Action, okay based on ranges, if valid save num
        elif type_ == '1':
            try:
                num = int(after_text)
            except ValueError:
                if self.can_be_negative() and after_text == '-':
                    return True
                return False
            if self.is_valid_range(num):
                self.last_valid = num
                return True
            return False
        return False

    def can_be_negative(self):
        """
        Tests whether this given entry widget can have a negative number

        :return: Whether or not the entry can have a negative number
        """
        return (self.low is None) or (self.low < 0)

    def is_valid_range(self, num):
        """
        Tests whether the given number is valid for this entry widgets range

        :param num: The number to range test

        :return: Whether or not the number is in range
        """
        return _NumberCheck.in_range(num, self.low, self.high)

    @staticmethod
    def in_range(num, low, high):
        """
        Tests whether or not a number is within a specified range inclusive

        :param num: The number to test if its in the range
        :param low: The minimum of the range
        :param high: The maximum of the range

        :return: Whether or not the number is in the range
        """
        if (low is not None) and (num < low):
            return False
        if (high is not None) and (num > high):
            return False
        return True


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    widget = ttk.Spinbox(root, justify=tk.CENTER, from_=-5, to_=10)
    widget.pack(padx=10, pady=10)
    int_validate(widget)
    root.mainloop()
