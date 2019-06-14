import re
import sys

import six
import logging


class Transductor(object):
    """
    A transductor is an automaton that performs rewrites as it parses text.

    Equiped with an additional stack. Transductor can be use to process and rewrite arbitray complex languages.

    The transition table as the following format
    {
    "state": [
                (match_text, replace_text_or_callable, target_state_operations)
             ]
    }

    where
       - match text is a regexp
       - replace_text or callable is a string or a callable or None to keep current text
       - target_state is a state, the '#push' or '#pop' to push current state or pop the state on the stack eventually
                       comma separated, typically '#push,newstate' to push current state and jump to a new state

    """

    def __init__(self, transition_table, initial_state=None):
        self.transition_table = transition_table
        self.initial_state = (initial_state is None) and (
            'a' if 'a' in transition_table else transition_table.keys()[0]) or initial_state
        self.stack = []

    def process(self, t, max_read_ahead=12, raise_on_empty_stack_pop=False):
        lt = len(t)
        cursor_postion = 0
        output = u""
        current_state = self.initial_state
        self.compiled_table = {}
        for processed_state in self.transition_table.keys():
            self.compiled_table[processed_state] = [((rewrite_rule, re.compile(rewrite_rule[0], re.U))
                                                     if len(rewrite_rule) < 4 else
                                                     (rewrite_rule,
                                                      re.compile(rewrite_rule[0], re.U | eval(rewrite_rule[3]))))
                                                    for rewrite_rule in self.transition_table[processed_state]
                                                    ]
        while cursor_postion < lt:
            for compiled_rewrite_rule in self.compiled_table[current_state]:
                rewrite_rule = compiled_rewrite_rule[0]
                compiled_rule =compiled_rewrite_rule[1]
                match_group = compiled_rule.match(t, cursor_postion, cursor_postion + max_read_ahead)
                if match_group:
                    break

            if (not match_group):  # 1365
                # no match we simply rewrite an go to the next character
                output += t[cursor_postion]
                cursor_postion += 1
            else:
                if isinstance(rewrite_rule[1], six.string_types):
                    rewritten_text = rewrite_rule[1]
                elif callable(rewrite_rule[1]):  # in [ type(lambda x:x)]):
                    rewritten_text = rewrite_rule[1](match_group)
                else:
                    rewritten_text = match_group.group(0)
                lx = len(match_group.group(0))
                output += rewritten_text
                if len(rewrite_rule) > 2:
                    if rewrite_rule[2] is not None:
                        for target_state in str(rewrite_rule[2]).split(','):
                            if target_state == "#push":
                                self.stack.append(current_state)
                            elif target_state == "#pop":
                                try:
                                    current_state = self.stack.pop(-1)
                                except Exception:
                                    logging.warning("Transductor warning : POP from empty list \n")
                                    if raise_on_empty_stack_pop:
                                        raise
                            else:
                                current_state = target_state
                assert (lx > 0)
                cursor_postion += lx
        return output
