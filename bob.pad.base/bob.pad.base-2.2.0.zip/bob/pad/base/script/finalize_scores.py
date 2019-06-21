"""Finalizes the scores that are produced by spoof.py
"""
import click
import numpy
import logging
from bob.extension.scripts.click_helper import (
    verbosity_option, log_parameters)

logger = logging.getLogger(__name__)


@click.command(name='finalize-scores', epilog='''\b
Examples:
  $ bin/bob pad finalize_scores /path/to/scores-dev
  $ bin/bob pad finalize_scores /path/to/scores-{dev,eval}
''')
@click.argument('scores', type=click.Path(exists=True, dir_okay=False),
                nargs=-1)
@click.option('-m', '--method', default='mean',
              type=click.Choice(['mean', 'min', 'max']), show_default=True,
              help='The method to use when finalizing the scores.')
@verbosity_option()
def finalize_scores(scores, method, **kwargs):
    """Finalizes the scores given by spoof.py
    When using bob.pad.base, Algorithms can produce several score values for
    each unique sample. You can use this script to average (or min/max) these
    scores to have one final score per sample.

    The conversion is done in-place. The order of scores will change.
    """
    log_parameters(logger)

    mean = {'mean': numpy.nanmean, 'max': numpy.nanmax, 'min': numpy.nanmin}[method]

    for path in scores:
        new_lines = []
        with open(path) as f:
            old_lines = f.readlines()
            old_lines.sort()
        for i, line in enumerate(old_lines):
            uniq, s = line.strip().rsplit(maxsplit=1)
            s = float(s)
            if i == 0:
                last_line = uniq
                last_scores = []

            if uniq == last_line:
                last_scores.append(s)
            else:
                new_lines.append('{} {}\n'.format(
                    last_line, mean(last_scores)))
                last_scores = [s]

            last_line = uniq

        else:  # this else is for the for loop
            new_lines.append('{} {}\n'.format(last_line, mean(last_scores)))

        with open(path, 'w') as f:
            f.writelines(new_lines)
