import importlib


def test_import():
    """Should import library"""
    importlib.import_module('sloth_cli')
