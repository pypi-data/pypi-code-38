from unittest import mock

from jollyjumper.rules import get_link_enjambment
from jollyjumper.rules import get_sirrematic_enjambment
from jollyjumper.rules import get_sirrematic_orational_enjambment
from jollyjumper.rules import get_sirrematic_prepositional_before_noun_adjective_enjambment
from jollyjumper.rules import get_sirrematic_prepositional_enjambment
from jollyjumper.rules import get_sirrematic_prepositional_without_de_enjambment
from jollyjumper.rules import get_sirrematic_relation_words_conjunction_enjambment
from jollyjumper.rules import get_sirrematic_relation_words_determiners_enjambment
from jollyjumper.rules import get_sirrematic_relation_words_preposition_enjambment
from jollyjumper.rules import get_sirrematic_relation_words_verbs_enjambment
from jollyjumper.rules import get_sirrematic_with_verb_enjambment


class TokenMock(mock.MagicMock):
    _ = property(lambda self: mock.Mock(has_tmesis=self.has_tmesis,
                                        line=self.line))

    @staticmethod
    def is_ancestor(token):  # noqa
        return True

    @staticmethod
    def nbor():  # noqa
        return TokenMock()


def test_get_sirrematic_enjambment_adj_noun():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(pos_="NOUN")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'NOUN']


def test_get_sirrematic_enjambment_adv_noun():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(pos_="NOUN")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADV', 'NOUN']


def test_get_sirrematic_enjambment_adp_adj():
    previous_token = TokenMock(pos_="ADP")
    next_token = TokenMock(pos_="ADJ")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADP', 'ADJ']


def test_get_sirrematic_enjambment_adp_noun():
    previous_token = TokenMock(pos_="ADP")
    next_token = TokenMock(pos_="NOUN")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADP', 'NOUN']


def test_get_sirrematic_enjambment_adj_verb():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(pos_="ADV")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'ADV']


def test_get_sirrematic_enjambment_adv_verb():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(pos_="VERB")
    output = get_sirrematic_enjambment(previous_token, next_token)
    assert output == ['ADV', 'VERB']


def test_get_sirrematic_relation_words_preposition_enjambment_adp_dummy():
    previous_token = TokenMock(lower_="a", pos_="ADP", tag_="AdpType=Prep")
    next_token = TokenMock(pos_="dummy")
    output = get_sirrematic_relation_words_preposition_enjambment(previous_token, next_token)
    assert output == ['ADP', 'dummy']


def test_get_sirrematic_relation_words_conjunction_enjambment_conj_dummy():
    previous_token = TokenMock(lower_="a", pos_="CONJ", tag_="AdpType=Prep")
    next_token = TokenMock(pos_="dummy")
    output = get_sirrematic_relation_words_conjunction_enjambment(previous_token, next_token)
    assert output == ['CONJ', 'dummy']


def test_get_sirrematic_relation_words_determiners_enjambment_det_noun():
    previous_token = TokenMock(pos_="DET")
    next_token = TokenMock(pos_="NOUN")
    output = get_sirrematic_relation_words_determiners_enjambment(previous_token, next_token)
    assert output == ['DET', 'NOUN']


def test_get_sirrematic_relation_words_determiners_enjambment_det_adj():
    previous_token = TokenMock(pos_="DET")
    next_token = TokenMock(pos_="ADJ")
    output = get_sirrematic_relation_words_determiners_enjambment(previous_token, next_token)
    assert output == ['DET', 'ADJ']


def test_get_sirrematic_relation_words_determiners_enjambment_det_adv():
    previous_token = TokenMock(pos_="DET")
    next_token = TokenMock(pos_="ADV")
    output = get_sirrematic_relation_words_determiners_enjambment(previous_token, next_token)
    assert output == ['DET', 'ADV']


def test_get_sirrematic_relation_words_determiners_enjambment_det_det():
    previous_token = TokenMock(pos_="DET")
    next_token = TokenMock(pos_="DET")
    output = get_sirrematic_relation_words_determiners_enjambment(previous_token, next_token)
    assert output == ['DET', 'DET']


def test_get_sirrematic_with_verb_enjambment_aux_verb():
    previous_token = TokenMock(pos_="AUX")
    next_token = TokenMock(pos_="VERB")
    output = get_sirrematic_with_verb_enjambment(previous_token, next_token)
    assert output == ['AUX', 'VERB']


def test_get_sirrematic_with_verb_enjambment_verb_verb():
    previous_token = TokenMock(pos_="VERB")
    next_token = TokenMock(pos_="VERB")
    output = get_sirrematic_with_verb_enjambment(previous_token, next_token)
    assert output == ['VERB', 'VERB']


def test_get_sirrematic_orational_enjambment_adj_que():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="que", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_adj_cuyo():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="cuyo", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_adj_cuya():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="cuya", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_adj_cuyos():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="cuyos", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_adj_cuyas():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="cuyas", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_adj_donde():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="donde", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_que():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="que", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_cuyo():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="cuyo", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_cuya():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="cuya", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_cuyos():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="cuyos", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_cuyas():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="cuyas", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_noun_donde():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="donde", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_que():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="que", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_cuyo():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="cuyo", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_cuya():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="cuyas", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_cuyos():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="cuyos", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_cuyas():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="cuyas", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_orational_enjambment_adv_donde():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="donde", pos_="dummy", tag_="NumType")
    output = get_sirrematic_orational_enjambment(previous_token, next_token)
    assert output == ['ADV', 'dummy']


def test_get_sirrematic_relation_words_verbs_enjambment_none():
    previous_token = TokenMock(pos_="dummy")
    next_token = TokenMock(lower_="caca", pos_="dummy")
    output = get_sirrematic_relation_words_verbs_enjambment(previous_token, next_token)
    assert output is None


def test_get_sirrematic_relation_words_verbs_enjambment_aux_de():
    previous_token = TokenMock(pos_="AUX")
    next_token = TokenMock(lower_="de", pos_="dummy", tag_="AdpType=Prep")
    output = get_sirrematic_relation_words_verbs_enjambment(previous_token, next_token)
    assert output == ['AUX', 'PREP']


def test_get_sirrematic_relation_words_verbs_enjambment_aux_del():
    previous_token = TokenMock(pos_="AUX")
    next_token = TokenMock(lower_="del", pos_="dummy", tag_="AdpType=Prep")
    output = get_sirrematic_relation_words_verbs_enjambment(previous_token, next_token)
    assert output == ['AUX', 'PREP']


def test_get_sirrematic_relation_words_verbs_enjambmentverb_de():
    previous_token = TokenMock(pos_="VERB")
    next_token = TokenMock(lower_="de", pos_="dummy", tag_="AdpType=Prep")
    output = get_sirrematic_relation_words_verbs_enjambment(previous_token, next_token)
    assert output == ['VERB', 'PREP']


def test_get_sirrematic_relation_words_verbs_enjambment_verb_del():
    previous_token = TokenMock(pos_="VERB")
    next_token = TokenMock(lower_="del", pos_="dummy", tag_="AdpType=Prep")
    output = get_sirrematic_relation_words_verbs_enjambment(previous_token, next_token)
    assert output == ['VERB', 'PREP']


def test_get_sirrematic_prepositional_prep_before_noun_or_adjective_enjambment_root_prep():
    previous_token = TokenMock(dep_="ROOT", pos_="NOUN")
    next_token = TokenMock(lower_="dummy", pos_="dummy", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_before_noun_adjective_enjambment(previous_token,
                                                                           next_token)
    assert output == ['NOUN', 'PREP']


def test_get_sirrematic_prepositional_prep_before_noun_or_adjective_enjambment_nsubj_prep():
    previous_token = TokenMock(dep_="nsubj", pos_="NOUN")
    next_token = TokenMock(lower_="dummy", pos_="dummy", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_before_noun_adjective_enjambment(previous_token,
                                                                           next_token)
    assert output == ['NOUN', 'PREP']


def test_get_sirrematic_prepositional_prep_before_noun_or_adjective_enjambment_0_n_rights():
    previous_token = TokenMock(dep_="nsubj", pos_="NOUN")
    next_token = TokenMock(lower_="dummy", pos_="dummy", tag_="AdpType=Prep", n_rights=0)
    output = get_sirrematic_prepositional_before_noun_adjective_enjambment(previous_token,
                                                                           next_token)
    assert output is None


def test_get_sirrematic_prepositional_without_de_enjambment_noun_prep():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="dummy", pos_="PREP", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_without_de_enjambment(previous_token, next_token)

    assert output == ['NOUN', 'PREP']


def test_get_sirrematic_prepositional_without_de_enjambment_adj_prep():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="dummy", pos_="PREP", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_without_de_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'PREP']


def test_get_sirrematic_prepositional_enjambment_adj_prep():
    previous_token = TokenMock(pos_="ADJ")
    next_token = TokenMock(lower_="dummy", pos_="PREP", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_enjambment(previous_token, next_token)
    assert output == ['ADJ', 'PREP']


def test_get_sirrematic_prepositional_enjambment_adv_prep():
    previous_token = TokenMock(pos_="ADV")
    next_token = TokenMock(lower_="dummy", pos_="PREP", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_enjambment(previous_token, next_token)
    assert output == ['ADV', 'PREP']


def test_get_sirrematic_prepositional_enjambment_noun_prep():
    previous_token = TokenMock(pos_="NOUN")
    next_token = TokenMock(lower_="dummy", pos_="PREP", tag_="AdpType=Prep", n_rights=1)
    output = get_sirrematic_prepositional_enjambment(previous_token, next_token)
    assert output == ['NOUN', 'PREP']


def test_get_link_enjambment_root_dummy():
    previous_token = TokenMock(dep_="ROOT", pos_="dummy")
    next_token = TokenMock(pos_="dummy", tag_="AdpType=Prep", n_rights=1, head=previous_token)
    output = get_link_enjambment(previous_token, next_token)
    assert output == ['dummy', 'dummy']


def test_get_link_enjambment_nsubj_dummy():
    previous_token = TokenMock(dep_="ROOT", pos_="dummy")
    next_token = TokenMock(pos_="dummy", tag_="AdpType=Prep", n_rights=1, head=previous_token)
    output = get_link_enjambment(previous_token, next_token)
    assert output == ['dummy', 'dummy']
