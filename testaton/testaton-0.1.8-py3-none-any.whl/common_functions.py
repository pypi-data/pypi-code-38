import math
import numpy as np
from collections import namedtuple

def score(test, truth):
    """
    A function that computes statistical difference between test and truth.
    The score function takes two arrays of real numbers (test = data that is being tested) and (truth = the ground truth that
    you're comparing against) and computes a number of statistics that measure the difference between the two data sets.
    It returns a named tuple called Score with a number of attributes of the result. This function just computes the measures.
    Pass the result to print_score to show a nice version of the score.
    """
    assert(len(truth) == len(test))
    total_size = len(truth)
    difference = test - truth
    abs_difference = abs(difference)

    rmse = math.sqrt( ((truth - test) ** 2).sum() ) / len(test)
    std_dev = np.std(truth - test)
    mean = np.mean(difference)
    median = np.median(difference)
    abs_mean = np.mean(abs(difference))

    negative = difference[difference < 0]
    positive = difference[difference > 0]
    exact = difference[difference == 0]
    within_1 = abs_difference[abs_difference < 1]
    within_5 = abs_difference[abs_difference <= 5]
    within_10 = abs_difference[abs_difference <= 10]
    sum_test = sum(test)
    sum_truth = sum(truth)

    sum_diff = sum_test - sum_truth
    sum_diff_pc = (sum_diff / sum_truth) * 100

    assert(total_size == len(test))

    min_diff = min(difference)
    max_diff = max(difference)
    negative_count = len(negative)
    positive_count = len(positive)
    negative_pc = (negative_count / total_size) * 100
    positive_pc = (positive_count / total_size) * 100

    exact_count = len(exact)
    within_1_pc = (len(within_1) / total_size) * 100
    within_5_pc = (len(within_5) / total_size) * 100
    within_10_pc = (len(within_10) / total_size) * 100
    over_10_pc = 100 - within_10_pc

    assert(negative_count + positive_count + exact_count == len(difference))

    Score = namedtuple('Score', 'size rmse mean abs_mean median std_dev min max negative_pc positive_pc \
                       exact_count within_1_pc within_5_pc within_10_pc, over_10_pc sum_diff sum_diff_pc')

    return Score(total_size, rmse, mean, abs_mean, median, std_dev, min_diff, max_diff, negative_pc,
                 positive_pc, exact_count, within_1_pc, within_5_pc, within_10_pc, over_10_pc,
                 sum_diff, sum_diff_pc)