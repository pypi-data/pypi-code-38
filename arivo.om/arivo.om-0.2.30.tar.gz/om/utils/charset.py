# coding=utf-8
from __future__ import unicode_literals

import logging

import related


class CharsetConverter:
    def _upper_replacements(self, replacements):
        upper_replacements = []
        for replacement in replacements:
            try:
                c_from, c_to = replacement["from"], replacement["to"]
                upper_replacements.append({
                    "from": c_from.upper(),
                    "to": c_to.upper()
                })
            except (KeyError, ValueError, TypeError):
                self.log.exception("skipping incorrect configured replacement: {}".format(replacement))
                continue
        return upper_replacements

    def __init__(self, replacements, allowed_chars):
        self.log = logging.getLogger("charset")
        self.replacements = self._upper_replacements(replacements)
        self.allowed_chars = allowed_chars.upper()

    @classmethod
    def from_yaml(cls, charset):
        allowed_chars = charset.allowed
        replacements = [{"from": r.c_from, "to": r.c_to} for r in charset.replacements]
        return cls(replacements, allowed_chars)

    def _replace(self, text):
        for replacement in self.replacements:
            c_from, c_to = replacement.get("from"), replacement.get("to")
            text = text.replace(c_from, c_to)
        return text

    def _remove_unknown(self, text):
        return "".join(x for x in text if x in self.allowed_chars)

    def clean(self, text):
        return self._remove_unknown(self._replace(text.upper()))


@related.immutable
class Replacement(object):
    c_from = related.StringField(key="from", required=True)
    c_to = related.StringField(key="to", required=True)


default_replacements = [
    Replacement(c_from=c_from, c_to=c_to) for (c_from, c_to) in
    (("Ä", "A"), ("Ü", "U"), ("Ö", "O"), ("O", "0"), ("Q", "0"))
]


def CharsetField():
    return related.ChildField(Charset, required=False, default=Charset())


@related.immutable
class Charset(object):
    replacements = related.SequenceField(Replacement, default=default_replacements)
    allowed = related.StringField(default="0123456789abcdefghijklmnprstuvwxyz")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    charset = Charset(replacements=[{"from": 'ä', "to": 'a'}], allowed_chars="Ac")
    print(charset.clean("ÄAÖBCÄDD"))
    assert charset.clean("ÄAÖBCÄDD") == "AACA"
