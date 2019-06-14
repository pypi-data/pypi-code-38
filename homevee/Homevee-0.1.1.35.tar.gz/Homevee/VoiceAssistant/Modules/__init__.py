#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Utils.Database import Database


class VoiceModule():
    def __init__(self, priority=1):
        self.priority = priority

    def get_context_key(self) -> int:
        """
        Get the context key
        :return: the context key
        """
        raise None

    def get_priority(self) -> int:
        """
        Get the priority
        :return: the priority
        """
        return self.priority

    def get_pattern(self, db: Database) -> list:
        """
        Get the pattern
        :param db: the database connection
        :return: the pattern
        """
        return None

    def get_label(self) -> str:
        """
        Get the label
        :return: the label
        """
        return None

    def run_command(self, username: str, text: str, context: dict, db: Database = None):
        if db is None:
            db = Database()
        """
        Run the voice command
        :param username: the username of the calling user
        :param text: the voice command text
        :param context: the context data dict
        :param db: the database connection
        :return:
        """
        pass

    #helper functions
    def is_number(self, s: str) -> bool:
        """
        Checks if the given string is a number
        :param s: the string
        :return: true if the string is a number, false otherwise
        """
        try:
            float(s)
            return True
        except ValueError:
            return False