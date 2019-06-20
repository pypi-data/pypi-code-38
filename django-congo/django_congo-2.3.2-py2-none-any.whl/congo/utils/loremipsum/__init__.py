# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
import os
import random
import re
from unidecode import unidecode
from collections import namedtuple
from congo.utils.text import slugify

class BaseGenerator(object):

    RE_SPACE = re.compile(r"[\s]+", re.UNICODE)
    RE_NON_WORD = re.compile(r"[^ \w']", re.UNICODE)
    MIN_WORD_LEN = 2

    @classmethod
    def _get_file_path(cls, dirname, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'sources', dirname, '%s.txt' % filename)

    @classmethod
    def _escape(cls, text):
        text = force_text(text)
        text = cls.RE_SPACE.sub(" ", text) # Standardize spacing.
        text = cls.RE_NON_WORD.sub("", text) # Remove non-word characters.
        return unicode(text.lower().strip())

class Universal(BaseGenerator):
    DOMAINS = 'domains'
    LOGINS = 'logins'

    GENERATOR_NAMES = (DOMAINS, LOGINS)

    def __init__(self, generator):
        file_path = self._get_file_path('universal', generator)
        with open(file_path, 'r') as text_file:
            self.generator = [row.decode('utf-8').strip() for row in text_file.readlines()]

    def get_value(self):
        return random.choice(self.generator)

class JohnDoe(BaseGenerator):
    PL_MALE = 'pl_male'
    PL_FEMALE = 'pl_female'

    GENERATOR_DICT = {
        PL_MALE: ('pl', 'male'),
        PL_FEMALE: ('pl', 'female'),
    }

    def __init__(self, *args):
        generators = []

        for generator in args:
            if generator in self.GENERATOR_DICT.keys():
                generators.append(generator)

        if not generators:
            generators = self.GENERATOR_DICT.keys()

        NameGenerator = namedtuple('NameGenerator', ['first_names', 'last_names', 'language', 'sex'])

        self.generators = []

        for generator in generators:
            first_names_file = self._get_file_path('john_doe', '%s_first' % generator)
            with open(first_names_file, 'r') as text_file:
                text = text_file.read().decode('utf-8')
                first_names = self._escape(text).split()

            last_names_file = self._get_file_path('john_doe', '%s_last' % generator)
            with open(last_names_file, 'r') as text_file:
                text = text_file.read().decode('utf-8')
                last_names = self._escape(text).split()

            language, sex = self.GENERATOR_DICT[generator]

            self.generators.append(NameGenerator(first_names, last_names, language, sex))

    def _get_generator(self):
        return random.choice(self.generators)

    def _get_person(self):
        generator = self._get_generator()
        first_name = random.choice(generator.first_names).title()
        last_name = random.choice(generator.last_names).title()
        email = self._get_email(first_name, last_name)
        mobile_phone = self._get_mobile_phone(generator.language)
        return first_name, last_name, email, mobile_phone, generator.language, generator.sex

    def _get_email(self, first_name, last_name):
        if not hasattr(self, '_email_generator'):
            self._email_generator = Universal(Universal.LOGINS)
        if not hasattr(self, '_domain_generator'):
            self._domain_generator = Universal(Universal.DOMAINS)

        x = random.random()
        separator = random.choice(['', '.', '-', '_'])

        if x > .75:
            login = "%s%s%s" % (slugify(first_name), separator, slugify(last_name))
        elif x > .5:
            i = random.randrange(1970, 2010)
            login = "%s%s%s" % (slugify(first_name), separator, i)
        elif x > .25:
            i = random.randrange(1970, 2010)
            login = "%s%s%s" % (slugify(last_name), separator, i)
        else:
            i = random.randrange(1, 999)
            login = "%s%s" % (self._email_generator.get_value(), i)

        return "%s@%s" % (login, self._domain_generator.get_value())

    def _get_mobile_phone(self, language):
        if language == 'pl':
            prefix = '+48'
            start = random.choice(['501', '502', '503', '504', '505', '506', '601', '602', '603', '604', '605', '606', '607', '608'])
            end = ''.join([str(random.randint(0, 9)) for i in range(6)])

        return "%s%s%s" % (prefix, start, end)

    def get_first_name(self):
        generator = self._get_generator()
        return random.choice(generator.first_names).title()

    def get_last_name(self):
        generator = self._get_generator()
        return random.choice(generator.last_names).title()

    def get_full_name(self):
        return " ".join(self._get_person()[:2])

    def get_email(self):
        return self._get_person()[2]

    def get_person(self):
        Person = namedtuple('Person', ['first_name', 'last_name', 'email', 'mobile_phone', 'language', 'sex'])
        return Person(*self._get_person())

class LoremIpsum(BaseGenerator):
    LOREM_IPSUM = 'lorem_ipsum'
    PAN_TADEUSZ = 'pan_tadeusz'
    HAMLET = 'hamlet'
    GOSPODIN_PROKHARCHIN = 'gospodin_prokharchin'
    DER_ERLKONIG = 'der_erlkonig'

    GENERATOR_NAMES = (LOREM_IPSUM, PAN_TADEUSZ, HAMLET, GOSPODIN_PROKHARCHIN, DER_ERLKONIG)

    def __init__(self, generator = None):
        if generator is None or generator not in self.GENERATOR_NAMES:
            generator = self.LOREM_IPSUM

        self.words = []

        text_path = self._get_file_path('lorem_ipsum', generator)
        if os.path.exists(text_path):
            with open(text_path, 'r') as text_file:
                text = text_file.read().decode('utf-8')

                for word in self._escape(text).split():
                    if len(word) > self.MIN_WORD_LEN and word not in self.words:
                        self.words.append(word)

    @classmethod
    def _make_sentence(cls, sentence):
        return "%s%s." % (sentence[0].upper(), sentence[1:])

    def get_words(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 3, 5
            else:
                max_len = min_len

        num = random.randint(min_len, max_len)
        if num > len(self.words):
            num = len(self.words)
        return random.sample(self.words, num)

    def get_phrase(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 3, 5
            else:
                max_len = min_len

        sentence = ' '.join(self.get_words(min_len, max_len))
        return "%s%s" % (sentence[0].upper(), sentence[1:])

    def get_sentence(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 7, 12
            else:
                max_len = min_len

        sentence = ' '.join(self.get_words(min_len, max_len))
        return self._make_sentence(sentence)

    def get_sentences(self, num, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 7, 12
            else:
                max_len = min_len

        return [self.get_sentence(min_len, max_len) for i in range(num)]

    def get_paragraph(self, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 4, 6
            else:
                max_len = min_len

        return ' '.join(self.get_sentences(random.randint(min_len, max_len)))

    def get_paragraphs(self, num, min_len = None, max_len = None):
        if not max_len:
            if not min_len:
                min_len, max_len = 4, 6
            else:
                max_len = min_len

        return [self.get_paragraph(min_len, max_len) for i in range(num)]
