import pytest
from educalingoDictionary import EducalingoDictionary


@pytest.fixture(scope='function')
def educa_dict():
    dic = EducalingoDictionary()
    yield dic


@pytest.fixture(scope='function')
def instance_dict():
    dic = EducalingoDictionary()
    dic.set_language(lang="pt")
    dic.search_word("nascimento")
    yield dic


def test_language(educa_dict):
    educa_dict.set_language(lang="pt")
    assert "pt" == "pt"


def test_search(instance_dict):
    assert instance_dict.soup != None


def test_available_dictionaries(educa_dict):
    educa_dict.get_available_dictionaries()
    assert type(educa_dict.languages) == dict


def test_available_dictionaries2(educa_dict):
    dictionaries = educa_dict.get_available_dictionaries()
    languages = educa_dict.get_available_dictionaries()
    assert dictionaries == languages


def test_translations(instance_dict):
    translations = instance_dict.get_translations()
    assert type(translations) == dict


def test_synonyms(instance_dict):
    synonyms = instance_dict.get_synonyms()
    assert type(synonyms) == list


def test_words_that_end_like(instance_dict):
    words = instance_dict.get_words_that_end_like()
    assert type(words) == list


def test_words_that_begin_like(instance_dict):
    words = instance_dict.get_words_that_begin_like()
    assert type(words) == list


def test_words_that_rhyme(instance_dict):
    words = instance_dict.get_words_that_rhyme()
    assert type(words) == list


def test_grammatical_category(instance_dict):
    categories = instance_dict.get_grammatical_category()
    assert type(categories) == list
