from sklearn import metrics


class TagLevelEvaluator(object):
    def __init__(self):
        self.y_true = []
        self.y_pred = []

    def get_score(self, **kwargs):
        if 'average' not in kwargs:
            kwargs['average'] = 'weighted'
        return metrics.f1_score(self.y_true, self.y_pred, **kwargs)

    def process_one_batch(self, y_true, y_pred):
        self.y_true.extend(y_true)
        self.y_pred.extend(y_pred)


if __name__ == "__main__":
    evaluator = TagLevelEvaluator()
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
