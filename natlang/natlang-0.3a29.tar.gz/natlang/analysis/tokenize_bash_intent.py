import json
import re

str_nfa = re.compile(r'''
("[^"]*")|('([^'])*')|    # str
([^\s]+)    #other stuff
''', re.VERBOSE)

sbtk_nfa = re.compile(r'''
[a-zA-Z_][a-zA-Z0-9_]*| # word
[0-9]+| # num
.''', re.VERBOSE)


def proc_line(line):
    matches = str_nfa.finditer(line)
    result = []
    for m in matches:
        group = m.group()
        if isinstance(group, tuple):
            raise RuntimeError("Multiple match of group {}".format(group))
        if group.endswith("\'s"):
            if group[:-1]:
                result.append(group[:-2])
            result.append('s')
        elif group.endswith('.') or group.endswith(','):
            if group[:-1]:
                result.append(group[:-1])
            result.append(group[-1])
        else:
            result.append(group)

    tokens = []
    for tk in result:
        if re.match(r'[a-zA-Z][a-z]*', tk):
            tokens.append(tk.lower())
        else:
            tokens.append(tk)
            tokens.append('[')
            # subtoken splitting
            tokens.extend(sbtk_nfa.findall(tk))
            tokens.append(']')

    return tokens


IN_TMPL = '/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/{}.nl.filtered'
OUT_TMPL = '/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/{}.nl.filtered.tokens'

if __name__ == '__main__':
    for dataset in ['train', 'dev', 'test']:
        IN_PATH = IN_TMPL.format(dataset)
        OUT_PATH = OUT_TMPL.format(dataset)
        with open(IN_PATH) as in_f:
            all_tokens = []
            for l in in_f:
                tokens = proc_line(l)
                all_tokens.append(tokens)

        with open(OUT_PATH, 'w') as out_f:
            for tokens in all_tokens:
                out_f.write(json.dumps(tokens))
                out_f.write('\n')
