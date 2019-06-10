"""
Deterministic Finite Automata
Examples taken from Understanding Computation Chapter 2

Conversion to mermaid cretes directly graphable in html using mermaidjs
"""
import hydraseq as hd

class DFAstate:
    def __init__(self, transitions, init_state, accepting_states=[]):
        self.states = hd.Hydraseq('_')
        self.init_state = init_state
        self.acceptings = accepting_states
        self.transitions = transitions
        [self.states.insert(transition) for transition in self.expand_transitions(transitions)]
        self.reset()

    def get_active_states(self):
        return self.states.get_active_values()

    def in_accepting(self):
        """Return True if current state is one of accepting states"""
        return any([state in self.acceptings for state in self.states.get_active_values()])

    def reset(self, init_state=None):
        self.states.look_ahead(init_state if init_state else self.init_state)
        return self

    def event(self, e):
        self.states.hit([e], is_learning=False)
        self.states.look_ahead([[action.replace('^', '') for action in self.states.get_next_values()]])
        return self
 
    def read_string(self, str):
        self.reset()
        [self.event(char) for char in str]
        return self

    def expand_transitions(self, transitions):
        expanded = []
        for transition in transitions:
            trans_tup = transition.split()
            if len(trans_tup) == 3 and ',' in trans_tup[1]:
                for elem in trans_tup[1].split(','):
                    expanded.append("{} {} {}".format(trans_tup[0], elem, trans_tup[2]))
            else:
                expanded.append(transition)
        return expanded
    
    def convert_to_mermaid(self):
        """Takes a 'st1 a st2' list of transitions and generates a mermaid compatible
            string like 'st1((st1)) --a--> st2((st2))' """
        def _convert_line(str_line):
            line_tuple = str_line.split()
            if len(line_tuple) == 1:
                return "{}(({}))".format(line_tuple[0], line_tuple[0])
            else:
                start, action, final = line_tuple
                final = final.replace('^', '')
                return "{}(({})) --{}--> {}(({}))".format(start, start, action, final, final)

        return "\n".join([_convert_line(line) for line in self.transitions])

    def __str__(self):
        return "DFA state: {}, preds: {}".format(self.states.get_active_values(), self.states.get_next_values())
