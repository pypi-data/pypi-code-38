# coding: utf-8
"""Módulo para funciones de preprocesamiento de texto."""


def filtrar_cortas(texto, chars=0):
    """Filtra líneas en texto de longitud chars o inferior.

    Parameters
    ----------
    texto : str
        Texto que se quiere filtrar.
    chars : int
        Mínimo número de caracteres en una línea de texto.

    Returns
    -------
    str
       Texto filtrado.
    """
    filtrado = ""
    for linea in texto.splitlines():
        if len(linea) > chars:
            filtrado += linea + "\n"

    return filtrado

