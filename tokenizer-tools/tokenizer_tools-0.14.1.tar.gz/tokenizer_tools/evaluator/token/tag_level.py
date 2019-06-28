from tokenizer_tools.evaluator.token.base_evaluator import BaseEvaluator


class TagEvaluator(BaseEvaluator):
    def __init__(self, *args, **kwargs):
        super(TagEvaluator, self).__init__(*args, **kwargs)

    def process_one_batch(self, gold_data, test_data, *args, **kwargs):
        # type: (List[str], List[str]) -> None

        check_corpus_aligned = kwargs.get('check_corpus_aligned', False)

        gold_tag_list = gold_data
        test_tag_list = test_data

        gold_tag_list_len = len(gold_tag_list)
        test_tag_list_len = len(test_tag_list)

        if check_corpus_aligned:
            assert gold_tag_list_len == test_tag_list_len
        else:
            # using gold_tag_list as gold,
            # if test_tag_list is shorter, then padding None as tag
            # if test_tag_list is logger, just ignore the rest
            if test_tag_list_len < gold_tag_list_len:
                # change str to list
                test_tag_list = [i for i in test_tag_list]

                test_tag_list.extend(
                    [None] * (gold_tag_list_len - test_tag_list_len)
                )
            if test_tag_list_len > gold_tag_list_len:
                test_tag_list = test_tag_list[:gold_tag_list_len]

        # no matter what, here must be true
        assert len(gold_tag_list) == len(test_tag_list)

        tag_len = len(gold_tag_list)
        flag = True
        for i in range(tag_len):
            gold_tag = gold_tag_list[i]
            test_tag = test_tag_list[i]

            if test_tag != gold_tag:
                flag = False

            if test_tag in ('E', 'S'):
                self.wc_of_test += 1
                if flag:
                    self.wc_of_correct += 1
                flag = True

            if gold_tag in ('E', 'S'):
                self.wc_of_gold += 1


if __name__ == "__main__":
    tag_evaluator = TagEvaluator()
    tag_evaluator.process_one_batch(
        'BMEBE',
        'BESBE'
    )
    tag_evaluator.process_one_batch(
        'BMEBE',
        'BESBE'
    )

    score = tag_evaluator.get_score()
    print(score)
