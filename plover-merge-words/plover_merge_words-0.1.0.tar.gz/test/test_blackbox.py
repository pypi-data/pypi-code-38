from plover_build_utils.testing import blackbox_test
from plover.registry import registry
from plover.config import DEFAULT_SYSTEM_NAME
from plover import system

registry.update()
system.setup(DEFAULT_SYSTEM_NAME)

@blackbox_test
class TestsBlackbox:

    def test_merge_word(self):
        r'''
        "KAUPB": "{con^}",
        "T-PB": "{:merge:continue}"

        KAUPB   " con"
        T-PB    " continue"
        T-PB    " continue continue"
        '''

    def test_merge_equals_with_space(self):
        r'''
        "KW-L": "{:merge: =}",
        "SRAR": "variable",
        "SRAL": "value",
        "S-P": "{^ ^}"

        SRAR/KW-L/SRAL     " variable = value"
        */*/*              ""
        SRAR/S-P/KW-L/SRAL " variable = value"
        '''

    def test_merge_two_words(self):
        r'''
        "TEFT": "test",
        "-FT": "{:merge: of the}",
        "-F": "of",
        "-T": "the"

        TEFT/-FT/-FT  " test of the"
        '''
