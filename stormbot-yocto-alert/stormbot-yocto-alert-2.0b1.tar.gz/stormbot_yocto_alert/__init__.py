"""Fortune for stormbot"""
import sys
import random
import argparse
from yoctopuce import yocto_api
from yoctopuce import yocto_relay

from stormbot.bot import Plugin

class Yocto(Plugin):
    def __init__(self, bot, args):
        self._bot = bot
        self._sentences = args.fortune_dict.decode().splitlines()
        self._errmsg = yocto_api.YRefParam()
        if yocto_api.YAPI.RegisterHub("usb", self._errmsg) != yocto_api.YAPI.SUCCESS:
            raise OSError
        self._relay = yocto_relay.YRelay.FindRelay(args.yocto_target + ".relay1")

    @classmethod
    def argparser(cls, parser):
        parser.add_argument("--yocto-target", type=str, required=True, help="Yocto target")

    def cmdparser(self, parser):
        subparser = parser.add_parser('alert', bot=self._bot)
        subparser.set_defaults(command=self.run)
        subparser.add_argument("--ack", dest="ack", action="store_true", help="Acknowledge alert")

    def random(self):
        return random.choice(self._sentences)

    def run(self, msg, parser, args, peer):
        if not (self._relay.isOnline()):
            self._bot.write("Yocto isn't online")
            return

        if args.ack:
            self._relay.set_state(yocto_relay.YRelay.STATE_B)
        else:
            self._relay.set_state(yocto_relay.YRelay.STATE_A)
