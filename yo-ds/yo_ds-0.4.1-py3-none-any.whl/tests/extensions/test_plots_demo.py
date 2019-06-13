from tests.extensions.common import *
from yo_extensions.misc import *


class PlotDemoTest(TestCase):
    def test_mkbook(self):
        this_file_name = path('test_plots.py')
        lines = Query.file.text(this_file_name).to_list()
        insertion = Query.en(lines).with_indices().where(lambda z: not z.item.startswith('from')).first().index
        lines.insert(insertion,'class TestCase:')
        lines.insert(insertion+1,'    pass')
        lines = Query.en(lines).select(lambda z: z + "\n").to_list()
        lines.append('tc = TestPlots()')
        cells = [CELL_TEMPLATE(lines)]

        ts = TestPlots()
        Query.en(dir(ts)).where(lambda z: z.startswith('test')).select('tc.{0}()'.format).select(CELL_TEMPLATE).foreach(cells.append)

        nb = NOTEBOOK_TEMPLATE(cells)
        save_json(path('Plots demo.ipynb'), nb)


def NOTEBOOK_TEMPLATE(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.7"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }


def CELL_TEMPLATE(lines):
    return {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": lines
    }
