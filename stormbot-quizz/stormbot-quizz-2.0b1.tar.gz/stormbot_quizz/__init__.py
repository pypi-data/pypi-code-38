"""Quizz for stormbot"""
import sys
import random
import argparse
import json
import operator
import unicodedata
import re
from pkg_resources import resource_string

from stormbot.bot import Plugin

class Contestant:
    def __init__(self, jid):
        self.jid = jid
        self._good = 0
        self._bad = 0

    def answer(self, good):
        if good:
            self._good += 1
        else:
            self._bad += 1

        return good

    @property
    def resource(self):
        return self.jid

    @property
    def good(self):
        return self._good

    @property
    def bad(self):
        return self._bad

class Quizz(Plugin):
    BAD_ANSWER = ["nop", "try again", "lol", "maybe you should start thinking about what you say", "nice try"]
    GOOD_ANSWER = ["that's it", "ok I'll accept it", "one more point for you"]

    def __init__(self, bot, args):
        self._bot = bot
        self._quizz = json.loads(args.quizz_data)
        self._current_quizz_name = None
        self._current_question = None
        self._scores = None
        self._count = 0
        self._max = 10

    @classmethod
    def argparser(cls, parser):
        default_data = resource_string(__name__, 'data/quizz.json')
        parser.add_argument("--quizz-data", type=argparse.FileType('r'), default=default_data,
                            help="Data to use for quizz (default: quizz.json)")

    def cmdparser(self, parser):
        subparser = parser.add_parser('quizz', bot=self._bot)
        subparser.set_defaults(command=self.run)
        subcmd = subparser.add_subparsers()
        cmd_list = subcmd.add_parser('list')
        cmd_list.set_defaults(subcmd=self._list)
        cmd_start = subcmd.add_parser('start')
        cmd_start.set_defaults(subcmd=self._start)
        cmd_start.add_argument("quizz", type=str)
        cmd_start.add_argument("--count", type=int, default=10)
        cmd_answer = subcmd.add_parser('answer')
        cmd_answer.set_defaults(subcmd=self._answer)
        cmd_answer.add_argument("answer", type=str)
        cmd_stop = subcmd.add_parser('stop')
        cmd_stop.set_defaults(subcmd=self._stop)
        cmd_score = subcmd.add_parser('score')
        cmd_score.set_defaults(subcmd=self._score)
        cmd_score = subcmd.add_parser('next')
        cmd_score.set_defaults(subcmd=self._next)

    async def run(self, msg, parser, args, peer):
        args.subcmd(msg, args)

    def _list(self, msg, args):
        for quizz in self._quizz:
            self._bot.write(quizz)

    def _start(self, msg, args):
        if args.quizz not in self._quizz:
            self._bot.write("{} isn't a valid quizz. You, dumbass.".format(args.quizz))
            return

        if self._current_quizz_name is not None:
            self._bot.write("A quizz is already being played. Finish it first.")

        self._current_quizz_name = args.quizz
        self._scores = {}
        self._count = 0
        self._max = args.count

        self._question()

    def _stop(self, msg, args):
        if self._current_quizz is None:
            self._bot.write("We are not playing any quizz right now. Are you drunk?")

        self._finish()

    def _finish(self):
        self._current_quizz_name = None
        self._bot.write("Quizz is now finished.")
        self._score(None, None)
        winner = max(self._scores.values(), key=operator.attrgetter('good'))
        self._bot.write("Congratulation to {} who won this quizz".format(winner.resource))

    def _score(self, msg, args):
        self._bot.write("Score is:")
        for contestant in sorted(self._scores.values(), key=operator.attrgetter('good'), reverse=True):
            self._bot.write(" - {}: {}".format(contestant.resource, contestant.good))

    def _question(self):
        if self._count == self._max:
            self._finish()
            return

        self._count += 1
        self._current_question = random.choice(list(self._current_quizz["questions"].keys()))
        self._bot.write("Quizz {} ({}/{}): {}".format(self._current_quizz_name, self._count, self._max, self._current_question))

    def _answer(self, msg, args):
        if self._current_quizz is None:
            self._bot.write("Nice one. You are stupid enought to answer while we are not playing any quizz.")
            return

        jid = msg["from"].resource
        if jid not in self._scores:
            self._scores[jid] = Contestant(msg["from"].resource)

        contestant = self._scores[jid]

        valid = True
        for answer, reference in zip(args.answer.split(" "), self._current_answer.split(" ")):
            valid = valid and phonex(answer) == phonex(reference)

        if contestant.answer(valid):
            self._bot.write("{}: {}".format(contestant.resource, random.choice(self.GOOD_ANSWER)))
            self._question()
        else:
            self._bot.write("{}: {}".format(contestant.resource, random.choice(self.BAD_ANSWER)))

    def _next(self, msg, args):
        if self._current_quizz is None:
            self._bot.write("Nice one. You are stupid enought to try to skip a question while we are not playing any quizz.")
            return

        self._bot.write("Pussy, the answer was easy. It's {}.".format(self._current_answer))
        self._question()

    @property
    def _current_answer(self):
        return self._current_quizz["questions"][self._current_question]

    @property
    def _current_quizz(self):
        return self._quizz[self._current_quizz_name] if self._current_quizz_name is not None else None

def phonex(word):
    word = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('utf8')
    word = word.upper()
    word = word.replace('Y', 'I')
    word = re.sub(r'([^PCS])H', r'\1', word)
    word = word.replace(r'PH', r'F')
    word = re.sub(r'G(AI?[NM])', r'K\1', word)
    word = re.sub(r'[AE]I[NM]([AEIOU])', r'YN\1', word)
    word = word.replace('EAU', 'O')
    word = word.replace('OUA', '2')
    word = word.replace('EIN', '4')
    word = word.replace('AIN', '4')
    word = word.replace('EIM', '4')
    word = word.replace('AIM', '4')
    word = word.replace('É', 'Y')
    word = word.replace('È', 'Y')
    word = word.replace('Ê', 'Y')
    word = word.replace('AI', 'Y')
    word = word.replace('EI', 'Y')
    word = word.replace('ER', 'YR')
    word = word.replace('ESS', 'YS')
    word = word.replace('ET', 'YT')
    word = word.replace('EZ', 'YZ')
    word = re.sub(r'AN([^AEIOU1234])', r'1\1', word)
    word = re.sub(r'ON([^AEIOU1234])', r'1\1', word)
    word = re.sub(r'AM([^AEIOU1234])', r'1\1', word)
    word = re.sub(r'EN([^AEIOU1234])', r'1\1', word)
    word = re.sub(r'EM([^AEIOU1234])', r'1\1', word)
    word = re.sub(r'IN([^AEIOU1234])', r'4\1', word)
    word = re.sub(r'([AEIOUY1234])S([AEIOUY1234])', r'\1Z\2', word)
    word = word.replace('OE', 'E')
    word = word.replace('EU', 'E')
    word = word.replace('AU', 'O')
    word = word.replace('OI', '2')
    word = word.replace('OY', '2')
    word = word.replace('OU', '3')
    word = word.replace('CH', '5')
    word = word.replace('SCH', '5')
    word = word.replace('SH', '5')
    word = word.replace('SS', 'S')
    word = word.replace('SC', 'S')
    word = re.sub(r'C([EI])', r'S\1', word)
    word = word.replace('C', 'K')
    word = word.replace('Q', 'K')
    word = word.replace('QU', 'K')
    word = word.replace('GU', 'K')
    word = word.replace('GA', 'KA')
    word = word.replace('GO', 'KO')
    word = word.replace('GY', 'KY')
    word = word.replace('A', 'O')
    word = word.replace('D', 'T')
    word = word.replace('P', 'T')
    word = word.replace('J', 'G')
    word = word.replace('B', 'F')
    word = word.replace('V', 'F')
    word = word.replace('M', 'N')

    last_char = None
    uniq_word = ''
    for char in word:
        if last_char != char:
            uniq_word += char
        last_char = char
    word = uniq_word
    mapping = ['1', '2', '3', '4', '5', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'N', 'O', 'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
    numeric = []
    for char in word:
        numeric.append(mapping.index(char))

    phonex = 0.
    i = 1
    for value in numeric:
        phonex = value * 22 ** -i + phonex
        i = i + 1

    return phonex
