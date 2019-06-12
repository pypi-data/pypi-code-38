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


def docs_topicos(modelo, corpus):
    """Distribución de probabilidad de tópicos en cada documento.

    Parameters
    ----------
    modelo : gensim.models.ldamodel.LdaModel
        Modelo LDA entrenado.
    corpus : banrep.corpus.MiCorpus
       Corpus previamente inicializado con documentos.

    Returns
    -------
    pd.DataFrame
      Documentos X Tópicos.
    """
    data = (dict(doc) for doc in modelo[corpus])
    index = [doc._.get("doc_id") for doc in corpus.docs]

    return pd.DataFrame(data=data, index=index)


def topico_dominante(df):
    """Participación de tópicos como dominante en documentos.

   Parameters
   ----------
   df : pd.DataFrame
      Distribución de probabilidad de tópicos en cada documento.

   Returns
   -------
   pd.DataFrame
      Participación de cada tópico como dominante.
   """
    absolutos = df.idxmax(axis=1).value_counts()
    relativos = round(absolutos / absolutos.sum(), 4).reset_index()
    relativos.columns = ["topico", "docs"]

    return relativos


def palabras_probables(modelo, topico, n=15):
    """Palabras más probables en un tópico.

   Parameters
   ----------
   modelo : gensim.models.ldamodel.LdaModel
      Modelo LDA entrenado.
   topico : int
      Número del Tópico.
   n : int
      Cuantas palabras obtener.

   Returns
   -------
   pd.DataFrame
      Palabras y sus probabilidades.
    """
    data = modelo.show_topic(topico, n)
    df = pd.DataFrame(data=data, columns=["palabra", "probabilidad"])
    df = df.sort_values(by="probabilidad", ascending=False)

    df["topico"] = topico

    return df


def corpus_stats(corpus):
    """Estadísticas del corpus.

    Parameters
    ----------
    corpus : banrep.corpus.MiCorpus
       Corpus previamente inicializado con documentos.

    Returns
    -------
    pd.DataFrame
      Estadísticas de cada documento del corpus.
    """
    exts = corpus.exts_doc
    data = ([doc._.get(ext) for ext in exts] for doc in corpus.docs)
    stats = pd.DataFrame(data=data, columns=exts)

    return stats


def corpus_tokens(corpus):
    """Tokens del corpus.

    Parameters
    ----------
    corpus : banrep.corpus.MiCorpus
        Corpus previamente inicializado con documentos.

    Returns
    -------
    pd.DataFrame
        Estadisticas de cada token del corpus.
    """
    exts_token = list(corpus.exts_token)

    columnas = ["doc_id", "sent_id", "tok_id", "word", "pos"] + exts_token
    items = []

    for doc in corpus.docs:
        sent_id = 1

        for frase in corpus.frases_doc(doc):
            tok_id = 1
            for tok in frase:
                fila = [doc._.get("doc_id"), sent_id, tok_id, tok.lower_, tok.pos_]
                for ext in exts_token:
                    fila.append(tok._.get(ext))
                tok_id += 1

                items.append(fila)

            sent_id += 1

    return pd.DataFrame(items, columns=columnas)


def corpus_ngramed(corpus):
    """Tokens del corpus con ngramas.

    Parameters
    ----------
    corpus : banrep.corpus.MiCorpus
        Corpus previamente inicializado con documentos.

    Returns
    -------
    pd.DataFrame
        Estadisticas de cada token del corpus.
    """
    columnas = ["doc_id", "sent_id", "tok_id", "word"]
    items = []
    for doc in corpus.docs:
        sent_id = 1

        for frase in corpus.ngram_frases(doc):
            tok_id = 1
            for tok in frase:
                fila = [doc._.get("doc_id"), sent_id, tok_id, tok]
                tok_id += 1

                items.append(fila)

            sent_id += 1

    return pd.DataFrame(items, columns=columnas)


def frases_stats(corpus):
    """Estadísticas de frases.

    Parameters
    ----------
    corpus : banrep.corpus.MiCorpus
       Corpus previamente inicializado con documentos.

    Returns
    -------
    pd.DataFrame
      Estadísticas de cada frase del corpus.
    """
    exts_span = list(corpus.exts_span)
    exts_token = list(corpus.exts_token)

    columnas = ["doc_id", "sent_id"] + exts_span + exts_token
    items = []

    for doc in corpus.docs:
        sent_id = 1
        for sent in doc.sents:
            fila = [doc._.get("doc_id"), sent_id]
            for ext in exts_span:
                fila.append(sent._.get(ext))
            for ext in exts_token:
                fila.append(sum(tok._.get(ext) for tok in sent))

            items.append(fila)
            sent_id += 1

    return pd.DataFrame(items, columns=columnas)
