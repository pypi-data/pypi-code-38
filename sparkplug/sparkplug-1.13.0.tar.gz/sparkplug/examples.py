from __future__ import print_function
import os


class EchoConsumer(object):
    def __init__(self, channel, format=u'pid={pid} body={body}'):
        self.channel = channel
        self.format = format

    def __call__(self, msg):
        text = self.format.format(body=msg.body, pid=os.getpid())
        print(text)
        self.channel.basic_ack(msg.delivery_tag)


class Broken(object):
    def __init__(self, channel):
        self.channel = channel

    def __call__(self, msg):
        raise ValueError(msg)
