#---------------------------------
#
# Author: Caio Moraes
# Email: <caiomoraes.cesar@gmail.com>
# GitHub: MoraesCaio
#
# LAViD - Laboratório de Aplicações de Vídeo Digital
#
#---------------------------------

import argparse
from .cogroo4py.cogroo_interface import Cogroo
from .singleton import Singleton
from subprocess import PIPE, Popen
import time
import psutil
import re
from os import path


current_dir = path.dirname(path.abspath(__file__))


def find_server_proc():
    "Return a list of server processes."
    ls = []
    for p in psutil.process_iter(attrs=['cmdline']):
        if len(p.info['cmdline']) > 2 and\
                'cogroo4py.jar' in p.info['cmdline'][2]:
            ls.append(p)
    return ls


class Server(metaclass=Singleton):

    def __init__(cls, cogroo_path='cogroo4py/cogroo4py.jar'):

        if not find_server_proc():

            process = Popen(['java', '-jar', path.join(current_dir, cogroo_path)], stdout=PIPE)

            while True:

                output = process.stdout.readline()

                if 'gateway server started' in output.decode().lower() or \
                        process.poll() is not None:
                    break

                time.sleep(0.1)


class Lemma:

    prefixes = [
        'contra',
        'supra-',
        'super-',
        'arqui-',
        'supra',
        'super',
        'arqui',
        'ultra',
        'intra',
        'sobre',
        'hiper',
        'vice-',
        'anti-',
        'anti',
        'ambi',
        'ante',
        'endo',
        'hipo',
        'vice',
        'pré-',
        'pós-',
        'pre',
        'pos',
        'aná',
        'ana',
        'epí',
        'epi',
        'des',
        'com',
        'con',
        'sim',
        'sin',
        'ex-',
        'co',
        'si',
        'in',
        'an',
        'di',
        'bi',
        'im',
        'en',
        'em',
        'ex',
        're',
        'e',
        'a',
        '',
    ]

    vbs = {
        # 4 primeiros: ir; particípio ['-RA', '-D', '-SD', '-SR']
        # 'SR': ['-PP'],
        # 'HV': ['-P', '-PP', '-AN-F', '-AN-F-P'],
        # 'ET': ['-PP'],
        # 'TR': ['-I', '-PP', '-AN-F', '-AN-F-P'],
        # 'VB': ['-AN', '-AN-F', '-AN-P', '-AN-F-P'],
    }

    poss_pro_f = {
        'minha': 'meu',
        'minhas': 'meus',
        'tua': 'teu',
        'tuas': 'teus',
        'sua': 'seu',
        'suas': 'seus',
        'nossa': 'nosso',
        'nossas': 'nossos',
        'vossa': 'vosso',
        'vossas': 'vossos',
    }

    object_pronouns = {
        'comigo': 'com eu',
        'contigo': 'com tu',
        'consigo': 'com tu',
        'conosco': 'com nós',
        'convosco': 'com vós',
    }

    def __init__(cls):
        cls.cogroo = Cogroo.Instance()
        cls.__server = Server()

    def _verbo(self, tag):

        is_verb = True
        if tag[1].startswith('HV'):
            tag[0] = 'haver'
            return tag, is_verb
        elif tag[1].startswith('ET'):
            tag[0] = 'estar'
            return tag, is_verb
        elif tag[1].startswith('TR'):
            tag[0] = 'ter'
            return tag, is_verb
        elif tag[1].startswith('SR'):  # and\
                # not tag[1].endswith(self.vbs['SR']):

            if not tag[0].startswith('f'):
                tag[0] = 'ser'
            # ser / ir
            else:
                tag[0] = self.lemmatize(tag[0])

            return tag, is_verb
        # VB
        else:

            lemma = self.lemmatize(tag[0])

            # successful or did not make difference
            if lemma.endswith('r') or tag[0] == lemma:
                tag[0] = lemma
                return tag, is_verb

            # failed to lemmatize
            is_verb = False
            return tag, is_verb

    def _special_case(self, tag):

        # ções -> ção; ços|çaís -> ço|çaí
        is_special_case = True

        if 'ç' in tag[0][-4:]:

            if tag[0].endswith('ões'):
                tag[0] = tag[0][:-3] + 'ão'
            elif tag[0].endswith('s'):
                tag[0] = tag[0][:-1]
            else:
                is_special_case = False

        elif 'mento' in tag[0][-6:]:
            if tag[0].endswith('s'):
                tag[0] = tag[0][:-1]

        elif 'dor' in tag[0][-5:]:
            sufixes = ['dores', 'doras', 'dora', 'dor']

            for sufix in sufixes:
                radical = tag[0].replace(sufix, '')
                # Fix for adoras, dor, dores, adora
                if len(radical) > 1:
                    if tag[0].endswith(sufix):
                        tag[0] = tag[0][:-len(sufix)] + 'dor'

        elif tag[0] == 'quaisquer':
            tag[0] = 'qualquer'

        elif tag[0] == 'quanta':
            tag[0] = 'quanto'

        else:
            is_special_case = False

        return tag, is_special_case

    def _contracao(self, tag):
        is_contracao = True

        if tag[0] == 'dalém':
            tag[0] = 'além'

        elif tag[0] in ['donde', 'aonde', 'daonde', 'donde']:
            tag[0] = 'onde'

        elif tag[0] in ['ao', 'aos', 'à', 'às']:
            tag[0] = ''

        elif tag[0].startswith('co'):
            if tag[0] in self.object_pronouns:
                tag[0] = self.object_pronouns[tag[0]]

        elif tag[1].startswith('P+'):
            plural = tag[0].endswith('s')
            tag[0] = self.lemmatize(tag[0]).split()[-1]
            if plural and not tag[0].endswith('s'):
                tag[0] += 's'
        else:
            is_contracao = False

        return tag, is_contracao

    def _artigo(self, tag):

        is_artigo = False
        if tag[0] in ['o', 'os', 'a', 'as']:
            tag[0] = ''
            is_artigo = True

        return tag, is_artigo

    def _pronome_possessivo(self, tag):
        is_pronome_possessivo = False

        if tag[1].startswith('PRO$'):
            is_pronome_possessivo = True

            if 'F' in tag[1] and tag[0] in self.poss_pro_f:
                tag[0] = self.poss_pro_f[tag[0]]

            plural = tag[0].endswith('s')
            tag[0] = self.lemmatize(tag[0])

            if plural and not tag[0].endswith('s'):
                tag[0] += 's'

        return tag, is_pronome_possessivo

    def _determiner(self, tag):
        is_determiner = True

        if self._artigo(tag)[1]:
            return tag, is_determiner

        elif tag[1].startswith('D'):
            if tag[1].startswith('D-UM') or\
                    tag[0] in ['um', 'uns', 'uma', 'umas']:
                tag[0] = ''
                return tag, is_determiner

            plural = tag[0].endswith('s')
            tag[0] = self.lemmatize(tag[0])

            if plural and not tag[0].endswith('s'):
                tag[0] += 's'
        else:
            is_determiner = False

        return tag, is_determiner

    def _preposicao(self, tag):
        is_preposicao = False

        if tag[1] == 'P':
            if tag[0] in ['em', 'de']:
                tag[0] = ''
                is_preposicao = True

        return tag, is_preposicao

    def _conjuncao(self, tag):
        is_conjuncao = False

        if tag[1] == 'CONJ':
            if tag[0] == 'e':
                tag[0] = ''
                is_conjuncao = True

        return tag, is_conjuncao

    # feitas -> feito; abraçados -> abraçado
    def _participio_passado(self, tag):
        is_participio_passado = False

        if tag[1].startswith('VB-AN'):
            is_participio_passado = True

            if tag[0].endswith('s'):
                tag[0] = tag[0][:-1]
            if tag[0].endswith('a'):
                tag[0] = tag[0][:-1] + 'o'

        return tag, is_participio_passado

    def lemmatize_aelius_tag(self, tag):

        if self._special_case(tag)[1]:
            # is_special_case -> return processed tag
            return tag

        if self._conjuncao(tag)[1]:
            return tag

        if self._pronome_possessivo(tag)[1]:
            return tag

        # contração may result in preposição or determiner
        self._contracao(tag)

        if self._preposicao(tag)[1]:
            return tag

        if self._determiner(tag)[1]:
            return tag

        if self._verbo(tag)[1]:
            return tag

        # Default
        if 'N-P' == tag[1] or\
                tag[1] == 'NUM-F' or\
                tag[1].startswith('ADJ') or\
                tag[1].startswith('OUTRO') or\
                tag[1].startswith('WPRO') or\
                tag[1].startswith('WD') or\
                tag[1].startswith('Q'):

            # nas -> 'em o'
            if not tag[1].startswith('P+'):
                # print(f'formatting {tag[0]} -> {self.lemmatize(tag[0])}')
                tag[0] = self.lemmatize(tag[0])

        return tag

    def lemmatize(self, word):
        for prefix in self.prefixes:
            if word.startswith(prefix):

                lemma = self.cogroo.lemmatize(word)
                prefix_lemma = self.cogroo.lemmatize(prefix)

                # RECOVERING PREFIX
                # fix for: 'pré-oral' -> 'pré - oral'
                if lemma.startswith(prefix_lemma):
                    lemma = re.sub(r'^' + prefix_lemma + r'\s?', prefix, lemma)
                # fix for: 'desligar' -> 'ligar'
                elif not lemma.startswith(prefix):
                    lemma = prefix + lemma

                return lemma

        return self.cogroo.lemmatize(word)

    def lemmatize_sentence(self, sentence):

        lemmas = []

        for word in sentence.split():
            lemmas.append(self.lemmatize(word))

        return ' '.join(lemmas)

    # lemmatize using only cogroo
    def lemmatize_cogroo(self, sentence):

        lemmas = []

        for word in sentence.split():
            lemmas.append(self.cogroo.lemmatize(word))

        return ' '.join(lemmas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phrase', help='Phrases.')
    parser.add_argument('-c', '--cogroo', action='store_true', help='Use only cogroo for lemmatizing.')
    parser.add_argument('-a', '--aelius', action='store_true', help='Lemmatize Aelius tag.')
    args, _ = parser.parse_known_args()

    if args.aelius:
        word = args.phrase.split()[-1]
        print(Lemma().lemmatize_aelius_tag([word, args.tag]))
    elif args.cogroo:
        print(Lemma().lemmatize_cogroo(args.phrase))
    else:
        print(Lemma().lemmatize_sentence(args.phrase))


if __name__ == '__main__':
    main()
