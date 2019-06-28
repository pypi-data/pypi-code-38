from tokenizer_tools.evaluator.token.base_evaluator import BaseEvaluator


class OffsetEvaluator(BaseEvaluator):
    def __init__(self, *args, **kwargs):
        super(OffsetEvaluator, self).__init__(*args, **kwargs)

    def process_one_batch(self, gold_offset_list, test_offset_list, *args, **kwargs):
        gold_offset_set = set(gold_offset_list)
        test_offset_set = set(test_offset_list)

        common_offset = gold_offset_set.intersection(test_offset_set)

        self.wc_of_correct += len(common_offset)
        self.wc_of_test += len(test_offset_list)
        self.wc_of_gold += len(gold_offset_list)


if __name__ == "__main__":
    evaluator = OffsetEvaluator()
    evaluator.process_one_batch(
        ['我是谁', '呢呢'],
        ['我是', '谁', '呢呢']
    )
    evaluator.process_one_batch(
        ['我是谁', '呢呢'],
        ['我是', '谁', '呢呢']
    )

    score = evaluator.get_score()
    print(score)
