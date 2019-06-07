# coding: utf8
import re
import string

import unidecode


def normalize_text(text):
    """
    Normalize text by deleting punctuations, extra spaces, and lowering characters.
    
    Parameters
    ----------
    text : string
        Text to clean

    Returns
    -------
    clean_text: string
    Cleaned text

    """
    clean_text = unidecode.unidecode(text).lower()
    clean_text = re.sub('[' + string.punctuation + ']', '', clean_text).strip()
    return clean_text
