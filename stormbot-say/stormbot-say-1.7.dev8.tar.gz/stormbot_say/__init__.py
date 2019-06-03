"""TTS for stormbot"""
import subprocess
from gtts import gTTS
from tempfile import NamedTemporaryFile

from stormbot.bot import Plugin


class Say(Plugin):
    def __init__(self, bot, args):
        self._bot = bot
        self.lang = args.say_lang

    @classmethod
    def argparser(cls, parser):
        parser.add_argument("--say-lang", type=str, default="fr", help="Say lang (default: %(default)s)")

    def cmdparser(self, parser):
        subparser = parser.add_parser('say', bot=self._bot)
        subparser.set_defaults(command=self.run)
        subparser.add_argument("--lang", type=str, default=self.lang, help="Say lang (default: %(default)s)")
        subparser.add_argument("text", type=str, help="Text to say")

    async def run(self, raw_msg, parser, args, origin_peer):
        if origin_peer is None:
            for peer in self._bot.get_peers(self):
                self._bot.peer_forward_msg(self, peer, raw_msg)

        tts = gTTS(text=args.text, lang=args.lang)
        with NamedTemporaryFile() as f:
            tts.write_to_fp(f)
            f.flush()
            cmd = ['play', '-t', 'mp3', f.name]
            if not origin_peer:
                self._bot.write(args.text)
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
