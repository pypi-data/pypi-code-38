# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from tokenizer_tools.tagset.BMES import BMESEncoderDecoder


word_coding_pairs = (
    ('我', 'S'),
    ('我们', 'BE'),
    ('飞机票', 'BME'),
    ('东南西北', 'BMME'),
)


@pytest.mark.parametrize("input_word, output_tags", word_coding_pairs)
def test_encode_word(input_word, output_tags):
    bmes_encoder_decoder = BMESEncoderDecoder()

    tags = bmes_encoder_decoder.encode_word(input_word)

    pytest.helpers.assert_sequence_equals(tags, output_tags)


@pytest.mark.parametrize(
    "word_list, gold_tags_list",
    (list(zip(*word_coding_pairs)),)
)
def test_encode_word_list(word_list, gold_tags_list):
    bmes_encoder_decoder = BMESEncoderDecoder()

    test_tags_list = bmes_encoder_decoder.encode_word_list(word_list)

    pytest.helpers.assert_sequence_equals(test_tags_list, gold_tags_list)


test_encode_word_list_as_string_parametrize = (
    (
        list(zip(*word_coding_pairs))[0],
        ''.join(list(zip(*word_coding_pairs))[1])
    ),
)


@pytest.mark.parametrize(
    "word_list, gold_str",
    test_encode_word_list_as_string_parametrize
)
def test_encode_word_list_as_string(word_list, gold_str):
    bmes_encoder_decoder = BMESEncoderDecoder()

    test_str = bmes_encoder_decoder.encode_word_list_as_string(word_list)

    pytest.helpers.assert_sequence_equals(test_str, gold_str)


test_decode_char_tag_pair_parametrize = (
    (list(zip(*[''.join(i) for i in zip(*word_coding_pairs)])), [i[0] for i in word_coding_pairs]),
)


@pytest.mark.parametrize("char_tag_pair, gold_word_list", test_decode_char_tag_pair_parametrize)
def test_decode_char_tag_pair(char_tag_pair, gold_word_list):
    bmes_encoder_decoder = BMESEncoderDecoder()

    test_word_list = bmes_encoder_decoder.decode_char_tag_pair(char_tag_pair)

    pytest.helpers.assert_sequence_equals(test_word_list, gold_word_list)


test_encode_word_with_addition_m_tag_num_parametrize = (
    (1, 'A' * 1, 'S'),
    (1, 'A' * 2, 'BE'),
    (1, 'A' * 3, 'BM1E'),
    (1, 'A' * 4, 'BM1ME'),
    (1, 'A' * 5, 'BM1MME'),

    (2, 'A' * 1, 'S'),
    (2, 'A' * 2, 'BE'),
    (2, 'A' * 3, 'BM1E'),
    (2, 'A' * 4, 'BM1M2E'),
    (2, 'A' * 5, 'BM1M2ME'),

    (3, 'A' * 1, 'S'),
    (3, 'A' * 2, 'BE'),
    (3, 'A' * 3, 'BM1E'),
    (3, 'A' * 4, 'BM1M2E'),
    (3, 'A' * 5, 'BM1M2M3E'),
    (3, 'A' * 6, 'BM1M2M3ME'),
)

@pytest.mark.parametrize("addition_m_tag_num, word, gold_tags", test_encode_word_with_addition_m_tag_num_parametrize)
def test_encode_word_with_addition_m_tag_num(addition_m_tag_num, word, gold_tags):
    bmes_encoder_decoder = BMESEncoderDecoder(addition_m_tag_num)

    test_tags = bmes_encoder_decoder.encode_word(word)

    pytest.helpers.assert_sequence_equals(test_tags, gold_tags)

