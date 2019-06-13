# coding: utf-8
"""Módulo para crear modelos de tópicos."""
import warnings

from gensim.models import CoherenceModel
from gensim.models.ldamodel import LdaModel


def crear_ldas(corpus, numeros, params):
    """Crea modelos LDA para diferente número de tópicos.

    Parameters
    ----------
    corpus : banrep.corpus.MiCorpus
       Corpus previamente inicializado con documentos.
    numeros: list (int)
        Diferentes #'s de tópicos.
    params: dict
        Parámetros requeridos en modelos LDA.

    Yields
    ------
    gensim.models.ldamodel.LdaModel
        Modelo LDA para un número de tópicos.
    """
    for n in numeros:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            yield LdaModel(corpus, num_topics=n, id2word=corpus.id2word, **params)


def calcular_coherencias(modelos, corpus, medida="c_v"):
    """Calcula Coherence Score de modelos de tópicos.

   Parameters
    ----------
   modelos : list (gensim.models.ldamodel.LdaModel)
      Modelos LDA para diferentes números de tópicos.
   corpus : banrep.corpus.MiCorpus
      Corpus previamente inicializado con documentos.
   medida : str
      Medida de Coherencia a usar (u_mass, c_v, c_uci, c_npmi).

   Yields
    ------
    float
      Coherencia calculada.
   """
    textos = [palabras for palabras in corpus.obtener_palabras()]
    for modelo in modelos:
        cm = CoherenceModel(
            model=modelo, texts=textos, dictionary=corpus.id2word, coherence=medida
        )

        yield cm.get_coherence()
