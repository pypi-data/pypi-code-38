class BaseEvaluator(object):
    def __init__(self, *args, **kwargs):
        self.wc_of_test = 0
        self.wc_of_gold = 0
        self.wc_of_correct = 0

    def process_one_batch(self, gold_data, test_data, *args, **kwargs):
        raise NotImplemented

    def get_score(self):
        # type: () -> Tuple(str, str, str)
        """

        :return: (precision, recall, f1)
        """

        print("WordCount from test result:", self.wc_of_test)
        print("WordCount from golden data:", self.wc_of_gold)
        print("WordCount of correct segs :", self.wc_of_correct)

        # 查全率
        precision = self.wc_of_correct / float(self.wc_of_test)
        # precision = self.wc_of_correct / float(self.wc_of_gold)

        # 查准率，召回率
        recall = self.wc_of_correct / float(self.wc_of_gold)

        precision_plus_recall = precision + recall

        # prevent precision_plus_recall is 0 for some case
        f1 = (2 * precision * recall) / precision_plus_recall if precision_plus_recall else 0

        metrics = {
            "RECALL": recall,
            "PRECISION": precision,
            "F1-MEASURE": f1
        }

        print("metrics = {}".format(metrics))

        return metrics
