import pandas as pd
import numpy as np
from matplotlib import pyplot as plt



def make_index(column):
    index = {c: i for i, c in enumerate(column.unique())}
    return column.apply(lambda x: index[x])


def make_table(data, value_column, bar_column, group_column, error_column):
    table = pd.DataFrame({'value': data[value_column]})

    if isinstance(table.value.iloc[0], pd.Interval):
        table = (table
            .value
            .apply(
            lambda i: pd.Series(
                [(i.right + i.left) / 2, (i.right - i.left) / 2],
                ['value', 'error']))
        )

    if bar_column is not None:
        table['bar'] = data[bar_column]
        table['bar_index'] = make_index(table.bar)
    else:
        table['bar'] = ''
        table['bar_index'] = 0

    if group_column is not None:
        table['group'] = data[group_column]
        table['group_index'] = make_index(table.group)
    else:
        table['group'] = ''
        table['group_index'] = 0

    if error_column is not None:
        table['error'] = data[error_column]
    elif 'error' not in table.columns:
        table['error'] = 0

    return table


def plot_bars(data, ax, value_column, bar_column, group_column=None, error_column=None,value_format='%.2f'):
    table = make_table(data, value_column, bar_column, group_column, error_column)
    if table.shape[0] == 0:
        return
    group_width = 1
    group_draw_width = 0.8
    bar_width = group_draw_width / (table.bar_index.max() + 1)
    table = table.assign(group_index = table.group_index.astype(int))
    table['x'] = table.group_index * group_width + table.bar_index * bar_width
    table['lower_y'] = table.value - table.error
    table['upper_y'] = table.value + table.error

    if value_format is not None:
        table['caption'] = table.apply(lambda x:
                                       (value_format % x.value) +
                                       (
                                           ('±' + value_format % x.error)
                                           if x.error != 0
                                           else ''
                                       )
                                       , axis=1)

    for bar_heading, bar_content in table.groupby('bar'):
        rects = ax.bar(
            list(bar_content.x),
            list(bar_content.upper_y),
            width=bar_width,
            label=bar_heading
        )

        if any(table.error > 0):
            ax.bar(
                list(bar_content.x),
                list(bar_content.lower_y),
                width=bar_width,
                color='white',
                alpha=0.6
            )

        if value_format is not None:

            for rect, caption in zip(rects, bar_content.caption):
                height = rect.get_height()
                ax.text(
                    rect.get_x() + rect.get_width() / 2.,
                    rect.get_height(),
                    caption,
                    ha='center', va='bottom')

    labels = table.groupby('group_index').apply(lambda x: x.group.iloc[0])
    ax.set_xlabel(group_column)
    ax.xaxis.set_ticks([x * group_width + group_draw_width / 2 - bar_width / 2 for x in labels.index])
    ax.xaxis.set_ticklabels(labels)

    ax.set_ylabel(value_column)
    return ax
