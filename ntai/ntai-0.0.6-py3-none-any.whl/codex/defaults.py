REPEAT_CHAR = '.'

FASTA_CHARS = set('actgrykmswbdhvn-')
ENCODE_ORDER = list('actgu')

INCLUDE_URACIL = False
INCLUDE_REPEAT = False

FASTA_ENCODEX = {
    'a': 'a',
    'c': 'c',
    't': 't',
    'g': 'g',
    'u': 'u',
    'r': 'ag',
    'y': 'ctu',
    'k': 'gtu',
    'm': 'ac',
    's': 'cg',
    'w': 'atu',
    'b': 'cgtu',
    'd': 'agtu',
    'h': 'actu',
    'v': 'acg',
    'n': 'actgu',
    '-': ''
}



FASTA_DECODEX = {
    'a'    : 'a',
    'c'    : 'c',
    't'    : 't',
    'g'    : 'g',
    'u'    : 'u',
    'ag'   : 'r',
    'ctu'  : 'y',
    'ct'   : 'y',
    'gtu'  : 'k',
    'gt'   : 'k',
    'ac'   : 'm',
    'cg'   : 's',
    'atu'  : 'w',
    'at'   : 'w',
    'cgtu' : 'b',
    'cgt'  : 'b',
    'agtu' : 'd',
    'agt'  : 'd',
    'actu' : 'h',
    'act'  : 'h',
    'acg'  : 'v',
    'acgtu': 'n',
    'acgt' : 'n',
    ''     : '-'
}
