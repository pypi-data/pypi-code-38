from unittest import mock

import jollyjumper.core
from jollyjumper.core import get_enjambment


class TokenMock(mock.MagicMock):
    _ = property(lambda self: mock.Mock(has_tmesis=self.has_tmesis,
                                        line=self.line))

    @staticmethod
    def is_ancestor(token):  # noqa
        return True

    @staticmethod
    def nbor():  # noqa
        return TokenMock()


def test_get_enjambment_tmesis(monkeypatch):
    def mockreturn(lang=None):
        return lambda _: [
            TokenMock(text="mi-\nra", i=0, is_punct=False, has_tmesis=True,
                      line=1)
        ]

    monkeypatch.setattr(jollyjumper.core, 'load_pipeline', mockreturn)
    enjambment = get_enjambment("text")
    assert enjambment == {1: {"type": 'tmesis', "on": ['mi', 'ra']}}


def test_get_enjambment_no_tmesis(monkeypatch):
    def mockreturn(lang=None):
        return lambda _: [
            TokenMock(text="mi\nra", i=0, is_punct=False, has_tmesis=False,
                      line=1)
        ]

    monkeypatch.setattr(jollyjumper.core, 'load_pipeline', mockreturn)
    enjambment = get_enjambment("text")
    assert enjambment == {}


def test_get_enjambment(monkeypatch):
    def mockreturn(lang=None):
        return lambda _: [
            TokenMock(n_rights=1, tag_="NumType", pos_="ADJ", text="mi", i=0,
                      is_punct=False, has_tmesis=False,
                      line=0),
            TokenMock(n_rights=1, tag_="NumType", pos_="SPACE", text="\n", i=1,
                      is_punct=False, has_tmesis=False,
                      line=0),
            TokenMock(n_rights=1, tag_="NumType", pos_="NOUN", text="casa", i=2,
                      is_punct=False, has_tmesis=False,
                      line=1)
        ]

    monkeypatch.setattr(jollyjumper.core, 'load_pipeline', mockreturn)
    enjambment = get_enjambment("text")
    assert enjambment == {0: {"type": 'sirrematic', "on": ['ADJ', 'NOUN']}}


def test_get_enjambment_empty(monkeypatch):
    def mockreturn(lang=None):
        return lambda _: [
            TokenMock(n_rights=1, tag_="NumType", pos_="ADJ", text="mi-", i=0,
                      is_punct=False, has_tmesis=False,
                      line=1),
            TokenMock(n_rights=1, tag_="NumType", pos_="SPACE", text="\n", i=0,
                      is_punct=False, has_tmesis=False,
                      line=1),
            TokenMock(n_rights=1, tag_="NumType", pos_="NOUN", text="ro", i=0,
                      is_punct=False, has_tmesis=False,
                      line=2)
        ]

    monkeypatch.setattr(jollyjumper.core, 'load_pipeline', mockreturn)
    enjambment = get_enjambment("text")
    assert enjambment == {}
