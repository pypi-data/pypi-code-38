import pandas as pd
import numpy as np

from math import log


def get_min_max_bracket_values(brackets):
    """
    # extract bracket values from index
    :param brackets:
    :return:
    """
    min_max_brackets = []
    if '$' in brackets.index[0]:
        for bracket in brackets.index:
            dollar_sign_position = [dpos for dpos, cval in enumerate(bracket) if cval == '$']
            if dollar_sign_position[0] == 0 and len(dollar_sign_position) == 1:
                minimum = ''.join([val for val in bracket if str.isdigit(val)])
                min_max_brackets.append([int(minimum), int(int(minimum)+int(minimum)/4)])
            elif dollar_sign_position[0] != 0 and len(dollar_sign_position) == 1:
                maximum = ''.join([val for val in bracket if str.isdigit(val)])
                min_max_brackets.append([0, int(maximum)])
            else:
                minimum = ''.join([val for val in bracket[:dollar_sign_position[1]] if str.isdigit(val)])
                maximum = ''.join([val for val in bracket[dollar_sign_position[1]:] if str.isdigit(val)])
                min_max_brackets.append([int(minimum), int(maximum)])
    else:
        for bracket in brackets.index:
            minimum = ''
            maximum = ''
            if bracket[0].isalpha():
                minimum = '0'
                maximum = ''.join([num for num in bracket if num.isdigit()])
            else:
                min_done = False
                for b in bracket:
                    if not min_done:
                        if b.isdigit():
                            minimum += b
                        if b.isspace():
                            min_done = True
                            continue
                    else:
                        if b.isdigit():
                            maximum += b
                        else:
                            continue
                if len(maximum) == 0:
                    maximum = int(minimum) + int(minimum) * 0.25
            min_max_brackets.append([int(minimum), int(maximum)])
    return min_max_brackets


def calculate_median_pareto(brackets: pd.Series) -> int:
    """
    http://en.wikipedia.org/wiki/Pareto_interpolation
    :param brackets:
    :return:
    """
    min_max_brackets = get_min_max_bracket_values(brackets)
    incomedata = [int(i) for i in brackets.values]
    bucket_tops = [i[1] for i in min_max_brackets]

    total = sum(incomedata)
    for i in range(1, len(incomedata)+1):
        if sum(incomedata[:i]) > (total / 2.0):
            lower_bucket = i - 2
            upper_bucket = i - 1
            if i == 17:
                break
            else:
                lower_sum = sum(incomedata[1:lower_bucket + 1])
                upper_sum = sum(incomedata[1:upper_bucket + 1])
                lower_perc = float(lower_sum) / total
                upper_perc = float(upper_sum) / total
                lower_income = bucket_tops[lower_bucket - 1]
                upper_income = bucket_tops[upper_bucket - 1]
                break
    if i == len(incomedata):
        return min_max_brackets[(len(incomedata)-1)][1]

    # now use pareto interpolation to find the median within this range
    if lower_perc == 0.0:
        sample_median = lower_income + ((upper_income - lower_income) / 2.0)
    else:
        theta_hat = (log(1.0 - lower_perc) - log(1.0 - upper_perc)) / (log(upper_income) - log(lower_income))
        k_hat = pow(
            (upper_perc - lower_perc) / ((1 / pow(lower_income, theta_hat)) - (1 / pow(upper_income, theta_hat))),
            (1 / theta_hat))
        sample_median = k_hat * pow(2, (1 / theta_hat))
    return int(sample_median)


def calculate_median_from_brackets(brackets: pd.Series) -> int:
    """
    This one is based on:
    http://support.mtabsurveyanalysis.com/sites/default/files/pdf_files/median.pdf
    :param brackets: Series object with bracket values in index
    :return: function comments
    """
    min_max_brackets = get_min_max_bracket_values(brackets)

    cumulative_brackets = [sum([b for i2, b in enumerate(brackets) if i2 < i]) + int(el) for i, el in enumerate(brackets)]
    sum_all = sum(brackets)
    sum_all_h = sum_all / 2
    pos = 0
    for i, el in enumerate(cumulative_brackets):
        if el > sum_all_h:
            pos = i
            break
    bracket_diff = sum_all_h - cumulative_brackets[pos - 1]
    bracket_diff_mf = cumulative_brackets[pos] - cumulative_brackets[pos - 1]
    res_diff = bracket_diff / bracket_diff_mf
    res_multiplication = res_diff * (min_max_brackets[pos][1] - min_max_brackets[pos][0])
    result = res_multiplication + min_max_brackets[pos][0]  # bottom range
    return int(result)


def calculate_mean_from_brackets(brackets: pd.Series) -> int:
    min_max_brackets = get_min_max_bracket_values(brackets)
    min_max_brackets_df = pd.DataFrame(min_max_brackets, columns=['a', 'b']).astype(int)
    min_max_brackets_df['midpoint'] = round((min_max_brackets_df['a'] + min_max_brackets_df['b']) / 2).astype(int)
    min_max_brackets_df['value_brackets'] = [b for i2, b in enumerate(brackets)]
    min_max_brackets_df['weight_count'] = min_max_brackets_df['value_brackets'] * min_max_brackets_df['midpoint']
    mean = round(sum(min_max_brackets_df['weight_count']) / sum(min_max_brackets_df['value_brackets']))
    return mean


if __name__ == '__main__':
    test_df_for_calc = pd.read_csv('tract_dollar_check.csv').transpose()
    test_df_for_calc.columns = test_df_for_calc.iloc[0]
    test_df_for_calc = test_df_for_calc.drop(test_df_for_calc.index[0])
    result_df = test_df_for_calc
    for ind, brack in test_df_for_calc.iterrows():
        result_df.loc[ind, 'median'] = calculate_median_from_brackets(brack)
        result_df.loc[ind, 'mean'] = calculate_mean_from_brackets(brack)
        result_df.loc[ind, 'pareto_median'] = calculate_median_pareto(brack)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(result_df)