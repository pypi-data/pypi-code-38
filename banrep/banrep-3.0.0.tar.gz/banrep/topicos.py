# coding: utf-8
"""Módulo para crear modelos de transformación de texto."""
import warnings

from gensim.models import CoherenceModel
from gensim.models.ldamodel import LdaModel
import pandas as pd


class Topicos:
    """Modelos de tópicos."""

    def __init__(self, corpus, kas, params, medida="c_v"):
        """Inicializa clase.

        Parameters
        ----------
        corpus : banrep.corpus.MiCorpus
            Corpus previamente inicializado con documentos.
        kas: list (int)
            Diferentes k tópicos para los cuales crear modelo.
        params: dict
            Parámetros requeridos en modelos LDA.
        medida : str
            Medida de Coherencia a usar (u_mass, c_v, c_uci, c_npmi).
        """
        self.corpus = corpus
        self.kas = kas
        self.params = params
        self.medida = medida

        self.modelos = [lda for lda in self.crear_ldas()]
        self.scores = [score for score in self.calcular_coherencias()]

        self.max_ch = max(self.scores)
        self.max_i = self.scores.index(self.max_ch)
        self.top_k = self.kas[self.max_i]

    def __repr__(self):
        return f"Modelos LDA para valores k en {self.kas}: mejor k={self.top_k} (Coherence={self.max_ch:.4f})"

    def __iter__(self):
        """Iterar devuelve cada modelo en orden de kas."""
        yield from self.modelos

    def crear_ldas(self):
        """Crea modelos LDA para diferente número de tópicos.

        Yields
        ------
        gensim.models.ldamodel.LdaModel
            Modelo LDA para un número de tópicos.
        """
        for k in self.kas:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                yield LdaModel(
                    self.corpus,
                    num_topics=k,
                    id2word=self.corpus.id2word,
                    **self.params,
                )

    def calcular_coherencias(self):
        """Calcula Coherence Score de modelos de tópicos.

        Yields
        ------
        float
            Coherencia calculada.
        """
        textos = [palabras for palabras in self.corpus.obtener_palabras()]
        for modelo in self.modelos:
            cm = CoherenceModel(
                model=modelo,
                texts=textos,
                dictionary=self.corpus.id2word,
                coherence=self.medida,
            )

            yield cm.get_coherence()

    def mejor_modelo(self):
        """Devuelve el mejor modelo según Coherence Score.

        Returns
        -------
        gensim.models.ldamodel.LdaModel
            Mejor modelo LDA según Coherence Score.
        """
        return self.modelos[self.max_i]

    def doc_topico(self, modelo):
        """Distribución de probabilidad de tópicos en cada documento.

        Parameters
        ----------
        modelo : gensim.models.ldamodel.LdaModel
            Modelo LDA entrenado.

        Returns
        -------
        pd.DataFrame
            Distribución de probabilidad de tópicos x documento.
        """
        data = (dict(doc) for doc in modelo[self.corpus])
        index = [doc._.get("doc_id") for doc in self.corpus.docs]

        return pd.DataFrame(data=data, index=index)

    def stats_topicos(self, modelo):
        """Distribución de probabilidad de tópicos y prevalencia en corpus.

        Parameters
        ----------
        modelo : gensim.models.ldamodel.LdaModel
            Modelo LDA entrenado.

        Returns
        -------
        tuple (pd.DataFrame, pd.Series)
            Distribución de probabilidad de tópicos y su Prevalencia.
        """
        dtm = self.doc_topico(modelo)
        dom = self._dominante(dtm)

        return dtm, dom

    @staticmethod
    def _dominante(df):
        """Participación de tópicos como dominante en documentos.

        Parameters
        ----------
        pd.DataFrame
            Distribución de probabilidad de tópicos x documento.

        Returns
        -------
        pd.Series
            Participación de cada tópico como dominante.
        """
        absolutos = df.idxmax(axis=1).value_counts()
        relativos = round(absolutos / absolutos.sum(), 3)
        relativos.index.name = "topico"

        return relativos

    @staticmethod
    def palabras_probables(modelo, n=15):
        """Distribución de probabilidad de palabras en tópicos.

        Parameters
        ----------
        modelo : gensim.models.ldamodel.LdaModel
            Modelo LDA entrenado.
        n : int
            Cuantas palabras obtener.

        Returns
        -------
        pd.DataFrame
            Palabras probables de cada tópico y sus probabilidades.
        """
        dfs = []
        for topico in range(modelo.num_topics):
            data = modelo.show_topic(topico, n)
            df = pd.DataFrame(data=data, columns=["palabra", "probabilidad"])
            df = df.sort_values(by="probabilidad", ascending=False)
            df["topico"] = topico
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)
