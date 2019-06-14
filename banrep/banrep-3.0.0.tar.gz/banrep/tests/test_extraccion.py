# coding: utf-8
"""Modulo para pruebas de extraccion."""
from banrep.extraccion import extraer_info, extraer_archivos, main

import pytest


def test_extraer_info():
    texto, metadata = extraer_info("bla.pdf")
    assert texto == None


def test_extraer_info_arg0():
    with pytest.raises(TypeError):
        texto, metadata = extraer_info()


def test_extraer_archivos_arg0():
    with pytest.raises(TypeError):
        n = extraer_archivos()


def test_extraer_archivos_arg1(tmp_path):
    with pytest.raises(TypeError):
        n = extraer_archivos(tmp_path)


def test_extraer_archivos(tmp_path):
    n = extraer_archivos(tmp_path, "textos")
    assert n == 0


def test_main_noargs():
        with pytest.raises(SystemExit):
                main()
