"""Quote for stormbot"""
import sys
import random
import shlex
import argparse

from stormbot.bot import Plugin
from stormbot.storage import Storage

class Quote(Plugin):
    def __init__(self, bot, args):
        self._bot = bot
        self._cache = Storage(args.quote_cache)
        if "quotes" not in self._cache:
            self._cache["quotes"] = {}
        self.quotes = self._cache["quotes"]

    @classmethod
    def argparser(cls, parser):
        parser.add_argument("--quote-cache", type=str, default="/var/cache/stormbot/quote.json", help="Cache file (default: %(default)s)")

    def cmdparser(self, parser):
        subparser = parser.add_parser('quote', bot=self._bot)
        subparser.add_argument("--all", action="store_true", help="Show all quotes")
        if 'stormbot_say' in sys.modules:
            subparser.add_argument("--say", dest="say", action="store_true", help="Say the quote")
        subparser.add_argument("author", nargs='?', help="Quote author")
        subparser.add_argument("quote", nargs='?', help="Quote")
        subparser.set_defaults(command=self.run)

    def store(self, author, quote):
        if author not in self.quotes:
            self.quotes[author] = []
        self.quotes[author].append(quote)
        self._bot.write("Your words are now engraved in the stones")

    def get(self, args):
        if len(self.quotes) == 0:
            self._bot.write("We don't have any quote yet, feel free to add some.")
            return None

        if args.all:
            return self.get_all(args)
        else:
            return self.get_one(args)

    def get_one(self, args):
        author = args.author if args.author is not None else random.choice(list(self.quotes.keys()))
        if author not in self.quotes or len(self.quotes[author]) < 1:
            self._bot.write("We don't have any quote for %s yet, feel free to add some." % author)
        else:
            quote = random.choice(self.quotes[author])
            self._bot.write("{} \"{}\"".format(author, quote))
            return quote

    def get_all(self, args):
        authors = [args.author] if args.author is not None else list(self.quotes.keys())
        for author in authors:
            for quote in self.quotes[author]:
                self._bot.write("{} \"{}\"".format(author, quote))
        return None

    async def run(self, msg, parser, args, peer):
        if args.quote is None:
            quote = self.get(args)
            if quote is not None and getattr(args, 'say', False):
                msg['body'] = f"{self._bot.nick}: say {shlex.quote(quote)}"
                say_args = ["say", quote]
                say_args = parser.parse_args(say_args)
                say_args.command(msg, parser, say_args, peer)
        else:
            self.store(args.author, args.quote)

if __name__ == "__main__":
    from stormbot.bot import main
    main(Quote)
