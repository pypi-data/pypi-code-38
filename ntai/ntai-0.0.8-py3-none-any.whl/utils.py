from .settings import (
    REPEAT_CHAR,
    FASTA_CHARS,
    ENCODE_ORDER,
    INCLUDE_URACIL,
    INCLUDE_REPEAT
)

def is_char(char:str) -> bool:
    '''
    Arguments:
        char (str): a string literal

    Returns:
        result (bool): whether or not the string literal is a single
            character
    '''
    is_str = type(char) is str
    is_sin = len(char) == 1
    return is_str and is_sin

def is_fasta(seq:str, fasta_chars:set=FASTA_CHARS) -> bool:
    '''
    Arguments:
        seq (str): a string literal to test if it represents a
            valid fasta sequence

        fasta_chars (set): the set of valid fasta character

    Returns:
        result (bool): whether or not seq is a valid fasta sequence
    '''
    seq_set = set(''.join(seq.lower()))
    val_set = set(fasta_chars)
    return set(seq_set).issubset(val_set)

def is_uracil(char:str) -> bool:
    '''
    Arguments:
        char (str): a string literal
    Returns:
        result (bool): whether or not char.lower() == 'u'
    '''
    return char.lower() == 'u'

def is_repeat(char):
    '''
    Notes:
        repeated masked regions are indicated by lower case letters
    Arguments:
        char (str): a string literal
    Returns:
        result (bool): whether or not char.islower()
    '''
    # lowercase letters indicate repeat-masked regions
    return char.islower()

def is_char_usable(
    char:str,
    include_uracil: bool  = INCLUDE_URACIL,
    include_repeat: bool  = INCLUDE_REPEAT,
    repeat_char: str      = REPEAT_CHAR,
    fasta_characters: set = FASTA_CHARS
)->bool:
    '''
    Arguments:
        char (str): a string literal
    Returns:
        result (bool):
    '''
    # cond_1 = is_char(char)
    # if not cond_1: return False
    cond_2 = (include_uracil or not is_uracil(char))
    if not cond_2: return False
    cond_3 = (include_repeat or not is_repeat(char, repeat_char))
    return cond_3
    # if not cond_3: return False
    # cond_4 = is_fasta(char, fasta_characters)
    # return cond_4
