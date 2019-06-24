"""
    A type of supervised learning algorithm, mostly used and preferred for classifications. The Idea is to split
    the data into tree format.
"""

from aitools.utils import util, constant


class DecisionTree:

    def __init__(self, independent_feature, dependent_features):
        self.tree = None
        self.independent_features = independent_feature
        self.dependent_features = dependent_features

    def build(self):
        self.tree = build_tree(util.build_feature_frame(self.independent_features, self.dependent_features))

    def predict(self, features, tree=None):

        if tree is None:
            tree = self.tree

        if isinstance(tree, Leaf):
            return tree.predictions

        return \
            self.predict(features, tree.true_branch) \
            if tree.question.match(features) \
            else self.predict(features, tree.false_branch)


class Leaf:

    def __init__(self, df):
        self.predictions = class_count(df)


class DecisionNode:

    def __init__(self, question, true_branch, false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch


def info_gain(left, right, current_uncertainty):
    p = float(len(left)) / (len(left) + len(right))
    return current_uncertainty - p * gini(left) - (1 - p) * gini(right)


def partition(df, question):
    true_rows, false_rows = [], []

    for row in df:
        true_rows.append(row) if question.match(row) else false_rows.append(row)

    return true_rows, false_rows


class Question:

    def __init__(self, col, val):
        self.col = col
        self.val = val

    def match(self, example):
        val = example[self.col]
        try:
            return val >= self.val if util.is_numeric(val) else val == self.val
        except TypeError:
            return False


def class_count(df):
    counts = {}

    for row in df:
        label = row[constant.INDEX_NEG_ONE]
        counts[label] = 1 if label not in counts else counts[label] + 1

    return counts


def gini(df):
    counts = class_count(df)
    impurity = 1

    for l in counts:
        prob_of_l = counts[l] / float(len(df))
        impurity -= prob_of_l ** 2

    return impurity


def find_best_split(df):
    best_gain = 0
    best_question = None
    current_uncertainty = gini(df)
    n_features = len(df[0]) - 1

    for col in range(n_features):

        values = set([row[col] for row in df])

        for val in values:

            question = Question(col, val)

            true_rows, false_rows = partition(df, question)

            if len(true_rows) == 0 or len(false_rows) == 0:
                continue

            gain = info_gain(true_rows, false_rows, current_uncertainty)

            if gain >= best_gain:
                best_gain, best_question = gain, question

    return best_gain, best_question


def build_tree(df):
    gain, question = find_best_split(df)

    if gain == 0:
        return Leaf(df)

    true_rows, false_rows = partition(df, question)

    true_branch = build_tree(true_rows)
    false_branch = build_tree(false_rows)

    return DecisionNode(question, true_branch, false_branch)
