# coding: utf-8
"""Modulo para pruebas de preprocesos."""

from banrep.preprocesos import filtrar_cortas

import pytest


def test_filtrar_cortas():
    texto = "Esta\nEsta sigue\nNo."
    chars = 5
    assert filtrar_cortas(texto, chars) == "Esta sigue\n"

def test_filtrar_cortas_arg0():
    with pytest.raises(TypeError):
        filtrar_cortas()
