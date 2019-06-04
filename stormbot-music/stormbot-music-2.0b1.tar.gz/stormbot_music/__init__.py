"""Play music from stormbot"""
import os
import shlex
import subprocess
import argparse
import logging
import aiohttp
import aiofiles
from stormbot.bot import Plugin, PeerCommand
from stormbot.storage import Storage


class Music(Plugin):
    dependencies = {'xep_0363'}

    def __init__(self, bot, args):
        self._bot = bot
        self._player = args.music_player
        self._path = os.path.abspath(args.music_path)
        self._uploaded = Storage(args.music_uploaded_cache)
        self._peer_path = args.music_peer_path
        self._default = args.music_default

        os.makedirs(self._peer_path, exist_ok=True)

    @classmethod
    def argparser(cls, parser):
        parser.add_argument("--music-player", type=str, default="paplay", help="Music player (default: %(default)s)")
        parser.add_argument("--music-path", type=str, default=os.getcwd(), help="Music file path (default: %(default)s)")
        parser.add_argument("--music-default", type=str, default=None, help="Default music file (default: %(default)s)")
        parser.add_argument("--music-peer-path", type=str, default="/var/cache/stormbot/music", help="Path where peer music file are stored (default: %(default)s)")
        parser.add_argument("--music-uploaded-cache", type=str, default="/var/cache/stormbot/music.json", help="Cache file keeping track of uploaded music files (default: %(default)s)")

    def safe_path(self, path):
        path = os.path.abspath(path)
        common_prefix = os.path.commonpath([path, self._path])
        return common_prefix == self._path

    def cmdparser(self, parser):
        subparser = parser.add_parser('music', bot=self._bot)
        subparser.set_defaults(command=self.run)
        subparser.add_argument("--volume", type=int, default=65536, help="Music player volume (default: %(default)i)")
        subparser.add_argument("--upload", help=argparse.SUPPRESS, action='store_true')
        subparser.add_argument("music", type=str, nargs='?', default=self._default,
                               help="Music to play (default: %(default)s)")

    async def run(self, msg, parser, args, peer):
        music = os.path.join(self._path, args.music)

        if peer is not None and args.upload:
            if args.music not in self._uploaded:
                url = await self._bot['xep_0363'].upload_file(music)
                self._uploaded[args.music] = url
            return self._uploaded[args.music]

        if not self.safe_path(music):
            if peer is None:
                self._bot.write("Don't try to mess with me !")
            return

        if not os.path.exists(music):
            if peer is None:
                self._bot.write("You have such shit taste I don't even have this song !")
            else:
                peer_path = os.path.join(self._peer_path, peer.nick)
                music = os.path.join(peer_path, args.music)

                if not os.path.exists(music):
                    logging.info(f"Missing music file: {args.music}. Requesting peer upload.")
                    iq = await self._bot.peer_send_command(self, peer,
                                                            f"music --upload {shlex.quote(args.music)}",
                                                            timeout=3600)
                    # TODO peer_send_command should return result string
                    # maybe we can create a future that exctract result string
                    result = iq['command'].xml.find("{%s}result" % PeerCommand.namespace)
                    if result is None:
                        logging.error("Missing result in command response")
                        return

                    if not os.path.isdir(peer_path):
                        os.mkdir(peer_path)
                    logging.info(f"Downloading {result.text} to {music}")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result.text) as resp:
                            f = await aiofiles.open(music, mode='wb')
                            await f.write(await resp.read())
                            await f.close()

        if peer is None:
            for peer in self._bot.get_peers(self):
                self._bot.peer_send_command(self, peer,
                                            f"music {shlex.quote(args.music)}",
                                            msg['mucnick'])
            self._bot.write("playing your favorite song out loud !")

        logging.info(f"Playing music file {music}")
        cmd = shlex.split(self._player) + [music]
        subprocess.Popen(cmd, stdin=None, stdout=None, stderr=None, close_fds=True)
