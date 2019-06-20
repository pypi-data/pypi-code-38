# -*- coding: utf-8 -*-
class BaseSMSBackend(object):
    """
    Base class for SMS backend implementations.
    Subclasses must at least overwrite send_messages().
    """

    def __init__(self, fail_silently = False, **kwargs):
        self.fail_silently = fail_silently

    def open(self):
        pass

    def close(self):
        pass

    def send_messages(self, sms_messages):
        raise NotImplementedError

    @classmethod
    def print_message(cls, message):
        print ""
        print "###################################"
        print message
        print "-----------------------------------"
        print message.content
        print "###################################"
        print ""
