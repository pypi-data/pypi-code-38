import json

IN_PATH = '/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash'
OUT_PATH = '/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash'
IN_SUFFIX = '.cm.filtered.tokens'
OUT_SUFFIX = '.jsonl'
NL_SUFFIX = '.nl.filtered.tokens'


def export(in_path, out_path, nl_path):
    with open(in_path, 'r') as in_f, open(out_path, 'w') as out_f, open(nl_path, 'r') as nl_f:
        lines = in_f.readlines()
        nls = nl_f.readlines()
        assert len(lines) == len(nls)
        for line, nl in zip(lines, nls):
            tokens = json.loads(line)

            nl_tokens = json.loads(nl)

            jsonl_entry = {'token': tokens, 'type': [], 'src': nl_tokens}
            out_f.write(json.dumps(jsonl_entry))
            out_f.write('\n')


for dataset in ['train', 'dev', 'test']:
    export('{}/{}{}'.format(IN_PATH, dataset, IN_SUFFIX),
           '{}/{}{}'.format(OUT_PATH, dataset, OUT_SUFFIX),
           '{}/{}{}'.format(IN_PATH, dataset, NL_SUFFIX))
