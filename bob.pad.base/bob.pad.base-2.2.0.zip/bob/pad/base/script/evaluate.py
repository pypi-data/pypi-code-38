"""Scripts that generate sevral metrics and plots for one or several
experiements
"""
import click
from bob.measure.script import common_options
from bob.extension.scripts.click_helper import verbosity_option
import bob.bio.base.script.commands as bio_commands
from . import (histograms, metrics, det, fmr_iapmr, epc)


@click.command()
@common_options.scores_argument(nargs=-1)
@common_options.legends_option()
@common_options.sep_dev_eval_option()
@common_options.table_option()
@common_options.eval_option()
@common_options.output_log_metric_option()
@common_options.output_plot_file_option(default_out='eval_plots.pdf')
@common_options.points_curve_option()
@common_options.lines_at_option()
@common_options.const_layout_option()
@common_options.figsize_option()
@common_options.style_option()
@common_options.linestyles_option()
@verbosity_option()
@click.pass_context
def evaluate(ctx, scores, evaluation, **kwargs):
    '''Runs error analysis on score sets

    \b
    1. Computes the threshold using either EER or min. HTER criteria on
       development set scores
    2. Applies the above threshold on evaluation set scores to compute the
       HTER, if a eval-score set is provided
    3. Reports error rates on the console
    4. Plots ROC, EPC, DET curves and score distributions to a multi-page PDF
       file


    You need to provide 2 score files for each biometric system in this order:

    \b
    * development scores
    * evaluation scores

    Examples:
        $ bob pad evaluate -v dev-scores

        $ bob pad evaluate -v scores-dev1 scores-eval1 scores-dev2
        scores-eval2

        $ bob pad evaluate -v /path/to/sys-{1,2,3}/scores-{dev,eval}

        $ bob pad evaluate -v -l metrics.txt -o my_plots.pdf dev-scores eval-scores
    '''
    # first time erase if existing file
    click.echo("Computing metrics...")
    ctx.invoke(metrics.metrics, scores=scores, evaluation=evaluation)
    if 'log' in ctx.meta and ctx.meta['log'] is not None:
        click.echo("[metrics] => %s" % ctx.meta['log'])

    # avoid closing pdf file before all figures are plotted
    ctx.meta['closef'] = False
    if evaluation:
        click.echo("Starting evaluate with dev and eval scores...")
    else:
        click.echo("Starting evaluate with dev scores only...")
    click.echo("Computing ROC...")
    # set axes limits for ROC
    ctx.forward(bio_commands.roc)  # use class defaults plot settings
    click.echo("Computing DET...")
    ctx.forward(det.det)  # use class defaults plot settings
    # the last one closes the file
    ctx.meta['closef'] = True
    click.echo("Computing score histograms...")
    ctx.meta['criterion'] = 'eer'  # no criterion passed in evaluate
    ctx.forward(histograms.hist)
    click.echo("Evaluate successfully completed!")
    click.echo("[plots] => %s" % (ctx.meta['output']))


@click.command()
@common_options.scores_argument(min_arg=2, force_eval=True, nargs=-1)
@common_options.legends_option()
@common_options.sep_dev_eval_option()
@common_options.table_option()
@common_options.output_log_metric_option()
@common_options.output_plot_file_option(default_out='vuln_plots.pdf')
@common_options.points_curve_option()
@common_options.lines_at_option()
@common_options.const_layout_option()
@common_options.figsize_option()
@common_options.style_option()
@common_options.linestyles_option()
@verbosity_option()
@click.pass_context
def vuln(ctx, scores, **kwargs):
    '''Runs error analysis on score sets for vulnerability studies

    \b
    1. Computes bob pad vuln_metrics
    2. Plots EPC, EPSC, vulnerability histograms, fmr vs IAPMR to a multi-page
       PDF file


    You need to provide 4 score files for each biometric system in this order:

    \b
    * licit development scores
    * licit evaluation scores
    * spoof development scores
    * spoof evaluation scores

    Examples:
        $ bob pad vuln -o my_epsc.pdf dev-scores1 eval-scores1

        $ bob pad vuln -D {licit,spoof}/scores-{dev,eval}
    '''
    # first time erase if existing file
    click.echo("Computing vuln metrics...")
    ctx.invoke(metrics.vuln_metrics, scores=scores, evaluation=True)
    if 'log' in ctx.meta and ctx.meta['log'] is not None:
        click.echo("[metrics] => %s" % ctx.meta['log'])

    # avoid closing pdf file before all figures are plotted
    ctx.meta['closef'] = False
    click.echo("Computing histograms...")
    ctx.meta['criterion'] = 'eer'  # no criterion passed in evaluate
    ctx.forward(histograms.vuln_hist)  # use class defaults plot settings
    click.echo("Computing EPC...")
    ctx.forward(epc.epc)  # use class defaults plot settings
    click.echo("Computing EPSC...")
    ctx.forward(epc.epsc)  # use class defaults plot settings
    click.echo("Computing FMR vs IAPMR...")
    ctx.meta['closef'] = True
    ctx.forward(fmr_iapmr.fmr_iapmr)  # use class defaults plot settings
    click.echo("Vuln successfully completed!")
    click.echo("[plots] => %s" % (ctx.meta['output']))
