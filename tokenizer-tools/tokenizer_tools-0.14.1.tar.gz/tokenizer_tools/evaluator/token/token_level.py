from tokenizer_tools.evaluator.token.base_evaluator import BaseEvaluator


class TokenEvaluator(BaseEvaluator):
    def __init__(self, *args, **kwargs):
        super(TokenEvaluator, self).__init__(*args, **kwargs)

    def generate_word_offset_list(self, word_list):
        offset_list = []

        start_index = 0
        for word in word_list:
            end_index = start_index + len(word)
            offset_list.append((start_index, end_index))

            start_index = end_index

        return offset_list

    def process_one_batch(self, gold_data, test_data, *args, **kwargs):
        gold_word_list = gold_data
        test_word_list = test_data

        gold_offset_list = self.generate_word_offset_list(gold_word_list)
        test_offset_list = self.generate_word_offset_list(test_word_list)

        common_offset = set(gold_offset_list).intersection(set(test_offset_list))

        self.wc_of_correct += len(common_offset)
        self.wc_of_test += len(test_offset_list)
        self.wc_of_gold += len(gold_offset_list)


if __name__ == "__main__":
    evaluator = TokenEvaluator()
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
