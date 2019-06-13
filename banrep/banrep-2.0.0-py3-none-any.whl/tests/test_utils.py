# coding: utf-8
"""Modulo para pruebas de utils."""
from banrep.utils import crear_directorio, iterar_rutas

import pytest


def test_crear_directorio(tmp_path):
    nombre = tmp_path.joinpath("output")
    nuevo = crear_directorio(nombre)

    assert nuevo.parent == tmp_path


def test_crear_directorio_arg0():
    with pytest.raises(TypeError):
        nuevo = crear_directorio()


def test_iterar_rutas(tmp_path):
    todas = iterar_rutas(tmp_path)
    assert len(list(todas)) == 0

def test_iterar_rutas_arg0():
    with pytest.raises(TypeError):
        todas = iterar_rutas()
