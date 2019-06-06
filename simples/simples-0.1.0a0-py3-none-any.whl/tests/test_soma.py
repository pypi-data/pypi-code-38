import pytest
from simples.soma import soma_inteiros, soma_reais

def test_soma_inteiros():
    assert soma_inteiros(5, 3) == 8, "Resultado deve ser 8"

def test_soma_reais():
    assert soma_reais(2.3, 6.2) == 8.5, "Resultado deve ser 8.5"