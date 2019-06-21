"""The main entry for bob pad commands.
"""
import click
from bob.measure.script import common_options
from bob.extension.scripts.click_helper import verbosity_option
import bob.bio.base.script.gen as bio_gen
import bob.measure.script.figure as measure_figure
from bob.bio.base.score import load
from . import pad_figure as figure
from .error_utils import negatives_per_pai_and_positives
from functools import partial

SCORE_FORMAT = (
    "Files must be 4-col format, see " ":py:func:`bob.bio.base.score.load.four_column`."
)
CRITERIA = (
    "eer",
    "min-hter",
    "far",
    "bpcer5000",
    "bpcer2000",
    "bpcer1000",
    "bpcer500",
    "bpcer200",
    "bpcer100",
    "bpcer50",
    "bpcer20",
    "bpcer10",
    "bpcer5",
    "bpcer2",
    "bpcer1",
    "apcer5000",
    "apcer2000",
    "apcer1000",
    "apcer500",
    "apcer200",
    "apcer100",
    "apcer50",
    "apcer20",
    "apcer10",
    "apcer5",
    "apcer2",
    "apcer1",
)


def metrics_option(
    sname="-m",
    lname="--metrics",
    name="metrics",
    help="List of metrics to print. Provide a string with comma separated metric "
    "names. For possible values see the default value.",
    default="apcer_pais,apcer,bpcer,acer,fta,fpr,fnr,hter,far,frr,precision,recall,f1_score",
    **kwargs
):
    """The metrics option"""

    def custom_metrics_option(func):
        def callback(ctx, param, value):
            if value is not None:
                value = value.split(",")
            ctx.meta[name] = value
            return value

        return click.option(
            sname,
            lname,
            default=default,
            help=help,
            show_default=True,
            callback=callback,
            **kwargs
        )(func)

    return custom_metrics_option


def regexps_option(
    help="A list of regular expressions (by repeating this option) to be used to "
    "categorize PAIs. Each regexp must match one type of PAI.",
    **kwargs
):
    def custom_regexps_option(func):
        def callback(ctx, param, value):
            ctx.meta["regexps"] = value
            return value

        return click.option(
            "-r",
            "--regexps",
            default=None,
            multiple=True,
            help=help,
            callback=callback,
            **kwargs
        )(func)

    return custom_regexps_option


def regexp_column_option(
    help="The column in the score files to match the regular expressions against.",
    **kwargs
):
    def custom_regexp_column_option(func):
        def callback(ctx, param, value):
            ctx.meta["regexp_column"] = value
            return value

        return click.option(
            "-rc",
            "--regexp-column",
            default="real_id",
            type=click.Choice(("claimed_id", "real_id", "test_label")),
            help=help,
            show_default=True,
            callback=callback,
            **kwargs
        )(func)

    return custom_regexp_column_option


@click.command()
@click.argument("outdir")
@click.option("-mm", "--mean-match", default=10, type=click.FLOAT, show_default=True)
@click.option(
    "-mnm", "--mean-non-match", default=-10, type=click.FLOAT, show_default=True
)
@click.option("-n", "--n-sys", default=1, type=click.INT, show_default=True)
@verbosity_option()
@click.pass_context
def gen(ctx, outdir, mean_match, mean_non_match, n_sys, **kwargs):
    """Generate random scores.
    Generates random scores in 4col or 5col format. The scores are generated
    using Gaussian distribution whose mean is an input
    parameter. The generated scores can be used as hypothetical datasets.
    Invokes :py:func:`bob.bio.base.script.commands.gen`.
    """
    ctx.meta["five_col"] = False
    ctx.forward(bio_gen.gen)


@common_options.metrics_command(
    common_options.METRICS_HELP.format(
        names="FtA, APCER, BPCER, FPR, FNR, FAR, FRR, ACER, HTER, precision, recall, f1_score",
        criteria=CRITERIA,
        score_format=SCORE_FORMAT,
        hter_note="Note that APCER = max(APCER_pais), BPCER=FNR, "
        "FAR = FPR * (1 - FtA), "
        "FRR = FtA + FNR * (1 - FtA), "
        "ACER = (APCER + BPCER) / 2, "
        "and HTER = (FPR + FNR) / 2. "
        "You can control which metrics are printed using the --metrics option. "
        "You can use --regexps and --regexp_column options to change the behavior "
        "of finding Presentation Attack Instrument (PAI) types",
        command="bob pad metrics",
    ),
    criteria=CRITERIA,
    epilog="""\b
More Examples:
\b
bob pad metrics -vvv -e -lg IQM,LBP -r print -r video -m fta,apcer_pais,apcer,bpcer,acer,hter \
/scores/oulunpu/{qm-svm,lbp-svm}/Protocol_1/scores/scores-{dev,eval}

See also ``bob pad multi-metrics``.
""",
)
@regexps_option()
@regexp_column_option()
@metrics_option()
def metrics(ctx, scores, evaluation, regexps, regexp_column, metrics, **kwargs):
    load_fn = partial(
        negatives_per_pai_and_positives, regexps=regexps, regexp_column=regexp_column
    )
    process = figure.Metrics(ctx, scores, evaluation, load_fn, metrics)
    process.run()


@common_options.roc_command(
    common_options.ROC_HELP.format(score_format=SCORE_FORMAT, command="bob pad roc")
)
def roc(ctx, scores, evaluation, **kwargs):
    process = figure.Roc(ctx, scores, evaluation, load.split)
    process.run()


@common_options.det_command(
    common_options.DET_HELP.format(score_format=SCORE_FORMAT, command="bob pad det")
)
def det(ctx, scores, evaluation, **kwargs):
    process = figure.Det(ctx, scores, evaluation, load.split)
    process.run()


@common_options.epc_command(
    common_options.EPC_HELP.format(score_format=SCORE_FORMAT, command="bob pad epc")
)
def epc(ctx, scores, **kwargs):
    process = measure_figure.Epc(ctx, scores, True, load.split, hter="ACER")
    process.run()


@common_options.hist_command(
    common_options.HIST_HELP.format(score_format=SCORE_FORMAT, command="bob pad hist")
)
def hist(ctx, scores, evaluation, **kwargs):
    process = figure.Hist(ctx, scores, evaluation, load.split)
    process.run()


@common_options.evaluate_command(
    common_options.EVALUATE_HELP.format(
        score_format=SCORE_FORMAT, command="bob pad evaluate"
    ),
    criteria=CRITERIA,
)
def evaluate(ctx, scores, evaluation, **kwargs):
    common_options.evaluate_flow(
        ctx, scores, evaluation, metrics, roc, det, epc, hist, **kwargs
    )


@common_options.multi_metrics_command(
    common_options.MULTI_METRICS_HELP.format(
        names="FtA, APCER, BPCER, FAR, FRR, ACER, HTER, precision, recall, f1_score",
        criteria=CRITERIA,
        score_format=SCORE_FORMAT,
        command="bob pad multi-metrics",
    ),
    criteria=CRITERIA,
    epilog="""\b
More examples:

\b
bob pad multi-metrics -vvv -e -pn 6 -lg IQM,LBP -r print -r video \
/scores/oulunpu/{qm-svm,lbp-svm}/Protocol_3_{1,2,3,4,5,6}/scores/scores-{dev,eval}

See also ``bob pad metrics``.
""",
)
@regexps_option()
@regexp_column_option()
@metrics_option(default="fta,apcer_pais,apcer,bpcer,acer,hter")
def multi_metrics(
    ctx, scores, evaluation, protocols_number, regexps, regexp_column, metrics, **kwargs
):
    ctx.meta["min_arg"] = protocols_number * (2 if evaluation else 1)
    load_fn = partial(
        negatives_per_pai_and_positives, regexps=regexps, regexp_column=regexp_column
    )
    process = figure.MultiMetrics(ctx, scores, evaluation, load_fn, metrics)
    process.run()
