from tokenizer_tools.evaluator.offset_evaluator import OffsetEvaluator
from tokenizer_tools.evaluator.token.token_level import TokenEvaluator
from tokenizer_tools.tagset.BMES import BMESEncoderDecoder
from tokenizer_tools.evaluator.token.tag_level import TagEvaluator
from tokenizer_tools.conll.reader import read_conll
from tokenizer_tools.tagset.NER.BILUO import BILUOSequenceEncoderDecoder


def evaluate_by_files_at_tag_level(test_file, gold_file):
    with open(test_file) as fd:
        test_line_list = fd.readlines()

    with open(gold_file) as fd:
        gold_line_list = fd.readlines()

    encoder = BMESEncoderDecoder()
    tag_evaluator = TagEvaluator()

    test_content = ' '.join([i.strip() for i in test_line_list])
    gold_content = ' '.join([i.strip() for i in gold_line_list])

    test_word_list = test_content.split()
    gold_word_list = gold_content.split()

    test_tags = encoder.encode_word_list_as_string(test_word_list)
    gold_tags = encoder.encode_word_list_as_string(gold_word_list)

    tag_evaluator.process_one_batch(gold_tags, test_tags)

    metrics = tag_evaluator.get_score()

    return metrics


def evaluate_by_files_at_token_level(test_file, gold_file):
    with open(test_file) as fd:
        test_line_list = fd.readlines()

    with open(gold_file) as fd:
        gold_line_list = fd.readlines()

    token_evaluator = TokenEvaluator()

    test_content = ' '.join([i.strip() for i in test_line_list])
    gold_content = ' '.join([i.strip() for i in gold_line_list])

    test_word_list = test_content.split()
    gold_word_list = gold_content.split()

    token_evaluator.process_one_batch(gold_word_list, test_word_list)

    metrics = token_evaluator.get_score()

    return metrics


def evaluate_NER_by_conll(input_file, gold_column_index=1, test_column_index=2):
    sentence_list = read_conll(input_file)
    decoder = BILUOSequenceEncoderDecoder()

    gold_tag_list = []
    test_tag_list = []
    for sentence in sentence_list:

        sentence_gold_tag = []
        sentence_test_tag = []
        for item_list in sentence:
            sentence_gold_tag.append(item_list[gold_column_index])
            sentence_test_tag.append(item_list[test_column_index])

        gold_tag_list.append(sentence_gold_tag)
        test_tag_list.append(sentence_test_tag)

    evaluator = OffsetEvaluator()

    for i in range(len(gold_tag_list)):
        gold_tag = gold_tag_list[i]
        test_tag = test_tag_list[i]

        gold_tag_offset = decoder.decode_to_offset(gold_tag)

        print(i)
        test_tag_offset = decoder.decode_to_offset(test_tag)

        evaluator.process_one_batch(gold_tag_offset, test_tag_offset)

    metrics = evaluator.get_score()
    return metrics


def evaluate_token_by_conll(input_file, gold_column_index=1, test_column_index=2):
    sentence_list = read_conll(input_file)
    decoder = BMESEncoderDecoder()

    gold_tag_list = []
    test_tag_list = []
    for sentence in sentence_list:

        sentence_gold_tag = []
        sentence_test_tag = []
        for item_list in sentence:
            sentence_gold_tag.append(item_list[gold_column_index])
            sentence_test_tag.append(item_list[test_column_index])

        gold_tag_list.append(sentence_gold_tag)
        test_tag_list.append(sentence_test_tag)

    evaluator = OffsetEvaluator()

    for i in range(len(gold_tag_list)):
        gold_tag = gold_tag_list[i]
        test_tag = test_tag_list[i]

        gold_tag_offset = decoder.decode_tag(gold_tag)

        print(i)
        test_tag_offset = decoder.decode_tag(test_tag)

        evaluator.process_one_batch(gold_tag_offset, test_tag_offset)

    metrics = evaluator.get_score()
    return metrics
