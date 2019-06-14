import sys
p = sys.platform[:4]
SYMBOL = {
    'finish': '¶',
    'end':'¾',
    'half':'½',
    'begin':'¼',
    'fail': '×',
    'bear':'🍺' if p == 'dar' else '■',
    'wait':'☕️' if p == 'dar' else ' ',
}