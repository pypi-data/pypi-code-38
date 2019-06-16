# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from .update_timer import UpdateTimer


class PrintStatus(object):
    def __init__(self, nl_on_clone=True, fp=sys.stdout):
        self.__update_timer = UpdateTimer()
        self.__first_status = True
        self.__last_printed_msg = None
        self.__last_msg = None
        self.__fp = fp
        self.__nl_on_close = nl_on_clone

    def close(self):
        if self.__last_msg is not None and self.__last_msg != self.__last_printed_msg:
            self.__print_status(True, self.__last_msg)

        if self.__nl_on_close:
            self.__print_to_out('\n')

    def __get_formatted_message(self, msg, *args, **kwargs):
        formatted_msg = ''

        if self.__last_printed_msg:
            spaces = len(self.__last_printed_msg)
            formatted_msg += '\r' + (' ' * spaces) + '\r'

        formatted_msg += msg.format(*args, **kwargs)

        if self.__first_status:
            formatted_msg = '\n' + formatted_msg

        return formatted_msg

    def __print_to_out(self, text):
        print(text, end='', file=self.__fp)
        self.__fp.flush()

    def __print_status(self, force, msg, *args, **kwargs):
        formatted_msg = self.__get_formatted_message(msg, *args, **kwargs)

        self.__last_msg = formatted_msg.strip()

        if self.__update_timer.can_update() or force:
            self.__print_to_out(formatted_msg)
            self.__last_printed_msg = self.__last_msg

        return True

    def print_status(self, msg, *args, **kwargs):
        printed_status = self.__print_status(False, msg, *args, **kwargs)

        if self.__first_status and printed_status:
            self.__first_status = False
