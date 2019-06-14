# coding: utf-8
"""Módulo para funciones de diagnóstico de datos usados y modelos generados."""
from collections import Counter

import pandas as pd


def verificar_oov(doc):
    """Encuentra tokens fuera de vocabulario (OOV) en un documento procesado.

   Parameters
   ----------
   doc: spacy.tokens.Doc

   Returns
   -------
   pd.DataFrame
      Tokens oov en frecuencia decreciente.
   """
    c = Counter(tok.text for tok in doc if tok.is_oov).items()
    df = pd.DataFrame(c, columns=["token", "freq"])
    df = df.sort_values(by="freq", ascending=False).reset_index(drop=True)

    return df
