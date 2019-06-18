#! /usr/bin/env python

# This file is part of neulang

# neulang - A language sitting on top of Python that executes pseudocode that's very close to natural language.

# @author Andrew Phillips
# @copyright 2017 Andrew Phillips <skeledrew@gmail.com>

# neulang is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.

# neulang is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.

# You should have received a copy of the GNU Affero General Public
# License along with neulang.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from builtins import bytes, str

import sys
import pdb
import re
from os.path import exists, join, dirname
import json


class Cerebrum():
    def __init__(self, populate=True):
        self._nuclei = {}
        self._thot_text = None
        self._thoughts = {
            'call_stack': [],
            'run_queue': [],
            'var_heap': {},
            'self': self,
            'special': {},
        }
        self._neurons = []
        if populate: self.make_neurons()

    def make_neurons(self, *nuclei):
        if not nuclei:
            nuclei = [
                globals()[elem] for elem in globals()
                if elem.startswith('neu_') and not elem in ['neu_main']
            ]
        cnt = 0

        for nucleus in nuclei:
            rx = nucleus()
            if not isinstance(rx, str): continue
            self._nuclei[rx] = nucleus
            cnt += 1
        return cnt

    def think(self):
        # usually a single neuron at the top
        if DEBUG: pdb.set_trace()
        self._thoughts['last'] = [
            neuron.fire(self._thoughts) for neuron in self._neurons
        ]
        return

    def read(self, text, style='org'):
        # convert text into neurons
        if DEBUG: pdb.set_trace()
        if not '*' in text: text = '* ' + text
        if text in ['-*quit*-', '-*exit*-']: sys.exit(0)
        self._thot_text = text
        neuron_list = []
        indent = r'^\*+ '
        if isinstance(text, str): text = text.strip().split('\n')
        level = ''

        for line in text:
            # create neurons from text
            match = re.match(indent, line)
            if not level and match: level = match.group(0)
            if not level: continue
            if not re.match(indent, line): continue
            neuron = Neuron(' '.join(line.split(' ')[1:]), self._nuclei)
            level_cnt = line.split(' ')[0].count('*')
            neuron_list.append([level_cnt, neuron])
        self._neurons = self._make_neuron_tree(neuron_list)
        return len(text)

    def _make_neuron_tree(self, neuron_list, level_cnt=1):
        # takes a list of neurons with levels, and recursively creates a tree of neurons
        tree = []
        sub_tree = []
        curr_level = level_cnt

        for neuron in neuron_list:

            if neuron[0] == level_cnt:

                if sub_tree:
                    # recurse and connect to assoc neuron
                    tree[-1].attach(
                        self._make_neuron_tree(sub_tree, level_cnt + 1))
                    sub_tree = []

                else:
                    tree.append(neuron[1])

            elif neuron[0] > level_cnt:
                # build sublist
                sub_tree.append(neuron)

            else:
                # shouldn't be here
                raise Exception('shouldn\'t be here')
        if sub_tree:
            tree[-1].attach(self._make_neuron_tree(sub_tree, level_cnt + 1))
        return tree


class Neuron():
    def __init__(self, text, nuclei):
        self._chain = []
        self._rx = ''
        self.build(text, nuclei)

    def __str__(self):
        return '{}'.format(self._rx)

    def __repr__(self):
        return '"Neuron(rx={})"'.format(self._rx)

    def build(self, text, nuclei):
        res = None
        self._text = text

        try:
            for rx in nuclei:
                match = re.match(rx, text)
                if not match: continue
                nucleus = nuclei[rx]
                self._rx = rx
                setattr(self, '_nucleus', nucleus.__get__(
                    self, self.__class__))
            res = self

        except Exception as e:
            res = e
        return res

    def _nucleus(self):
        # just a stub
        pass

    def parse(
            self,
            text, ):
        pass

    def attach(self, nodes):
        self._chain.extend(nodes)

    def fire(self, state):
        try:
            return self._nucleus(state)

        except Exception as e:

            if DEBUG:
                print(repr(e))
                pdb.post_mortem()

            else:
                state['special']['break_out'] -= 2

    def get_text(self):
        return self._text

    def get_chain(self):
        return self._chain

    def gen(self):
        pass


def neu_500_print(*args):
    rx = r'(print|say)( from)? (?P<What>[\w ]+)'
    if not args: return rx
    self, state = args
    text = self.get_text()
    what = re.match(rx, text).group('What')
    invoke = text.split(' ')[0]
    if what in ['it']:
        what = state['special'].get('last_value',
                                    'I dunno what to {}'.format(invoke))
    if 'from' in text and text.split(' ')[1] == 'from':
        what = state['var_heap'].get(
            what.replace(' ', '_'), 'Cannot find that one')
    print(what)
    return True


def neu_500_input(*args):
    rx = r'(get|read) (?P<Var>[\w ]+?)( with prompt (?P<Prompt>[\w ]+))? from( the)? user'
    if not args: return rx
    self, state = args
    vars = re.match(rx, self.get_text()).groupdict()
    prompt = vars.get('Prompt', None)
    if not prompt: prompt = 'enter something'
    value = input(prompt + ': ')
    state['var_heap'][vars.get('Var').replace(' ', '_')] = value
    state['special']['last_value'] = value
    return True


def neu_500_eval(*args):
    rx = r'evaluate (?P<Expr>[\w ]+)'
    if not args: return rx
    self, state = args
    expr = re.match(rx, self.get_text()).group('Expr')
    if expr in ['it']:
        expr = state['special'].get('last_value', 'Nothing to evaluate')
    state['self'].read(expr)
    state['self'].think()
    return True


def neu_500_loop(*args):
    rx = r'loop( for each (?P<Item>[\w ]+?) in (?P<Coll>[\w ]+)| while (?P<WCond>[\w ]+)| until (?P<UCond>[\w ]+))?'
    if not args: return rx
    self, state = args
    if DEBUG: pdb.set_trace()
    if not 'break_out' in state['special']: state['special']['break_out'] = 0
    text = self.get_text()
    v_dict = re.match(rx, text).groupdict()

    if text == 'loop':
        # infinite loop
        break_out = state['special']['break_out']
        state['special']['break_out'] += 2

        while True:

            for neuron in self._chain:
                # facilitate proper breaking between firing
                neuron.fire(state)
                if state['special']['break_out'] <= break_out: break

            if state['special']['break_out'] <= break_out:
                break


def load_nuclei(cere, path):
    # get nuclei from a script or dir of scripts
    factory = []


def create_cerebrum():
    return Cerebrum()


def neu_main():
    args = sys.argv
    global interact
    global DEBUG
    cere = Cerebrum()

    for pos, arg in enumerate(args):

        if pos > 0 and exists(arg):
            # script given; TODO: pass script args into script env
            script = open(args[1]).read()
            if DEBUG: pdb.set_trace()
            cere.read(script)
            cere.think()
            if not interact: return
            break

        elif arg in ['-c']:
            # command given
            script = args[pos + 1].replace('\\n', '\n')
            if DEBUG: pdb.set_trace()
            cere.read(script)
            cere.think()
            if not interact: return
            break

        elif arg in ['-i']:
            interact = True

        elif arg in ['-h', '--help', '-?']:
            return

        elif arg in ['-v', '--version']:
            print('neu {}'.format(__version__))
            return

        elif arg in ['-d']:
            DEBUG = True
            continue
    i_act_script = 'interact.org'
    cere.read(open(i_act_script).read())
    cere.think()


DEBUG = False

meta_file = join(dirname(__file__), 'meta.json')
if not exists(meta_file): open(meta_file, 'w').write('{}')
meta = json.load(open(meta_file))
__author__ = meta.get('author', 'skeledrew')
__version__ = meta.get('version', '0.0.1')

interact = False

if not __name__ == '__main__' and sys.argv[0] == '':
    # using interpreter
    interact = True

if __name__ == '__main__':
    neu_main()
