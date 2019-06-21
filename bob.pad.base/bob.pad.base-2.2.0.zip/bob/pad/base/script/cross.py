"""Prints Cross-db metrics analysis
"""
import click
import json
import jinja2
import logging
import math
import os
import yaml
from bob.bio.base.score.load import load_score, get_negatives_positives
from bob.extension.scripts.click_helper import (
    verbosity_option,
    bool_option,
    log_parameters,
)
from bob.measure import eer_threshold, farfrr
from bob.measure.script import common_options
from bob.measure.utils import get_fta
from gridtk.generator import expand
from tabulate import tabulate

logger = logging.getLogger(__name__)


@click.command(
    epilog="""\b
Examples:
  $ bin/bob pad cross 'results/{{ evaluation.database }}/{{ algorithm }}/{{ evaluation.protocol }}/scores/scores-{{ group }}' \
    -td replaymobile \
    -d replaymobile -p grandtest \
    -d oulunpu -p Protocol_1 \
    -a replaymobile_grandtest_frame-diff-svm \
    -a replaymobile_grandtest_qm-svm-64 \
    -a replaymobile_grandtest_lbp-svm-64 \
    > replaymobile.rst &
"""
)
@click.argument("score_jinja_template")
@click.option(
    "-d",
    "--database",
    "databases",
    multiple=True,
    required=True,
    show_default=True,
    help="Names of the evaluation databases",
)
@click.option(
    "-p",
    "--protocol",
    "protocols",
    multiple=True,
    required=True,
    show_default=True,
    help="Names of the protocols of the evaluation databases",
)
@click.option(
    "-a",
    "--algorithm",
    "algorithms",
    multiple=True,
    required=True,
    show_default=True,
    help="Names of the algorithms",
)
@click.option(
    "-n",
    "--names",
    type=click.File("r"),
    help="Name of algorithms to show in the table. Provide a path "
    "to a json file maps algorithm names to names that you want to "
    "see in the table.",
)
@click.option(
    "-td",
    "--train-database",
    required=True,
    help="The database that was used to train the algorithms.",
)
@click.option(
    "-pn",
    "--pai-names",
    type=click.File("r"),
    help="Name of PAIs to compute the errors per PAI. Provide a path "
    "to a json file maps attack_type in scores to PAIs that you want to "
    "see in the table.",
)
@click.option(
    "-g",
    "--group",
    "groups",
    multiple=True,
    show_default=True,
    default=["train", "dev", "eval"],
)
@bool_option("sort", "s", "whether the table should be sorted.", True)
@common_options.table_option()
@common_options.output_log_metric_option()
@verbosity_option()
@click.pass_context
def cross(
    ctx,
    score_jinja_template,
    databases,
    protocols,
    algorithms,
    names,
    train_database,
    pai_names,
    groups,
    sort,
    verbose,
    **kwargs
):
    """Cross-db analysis metrics
    """
    log_parameters(logger)

    names = {} if names is None else json.load(names)

    env = jinja2.Environment(undefined=jinja2.StrictUndefined)

    data = {
        "evaluation": [
            {"database": db, "protocol": proto}
            for db, proto in zip(databases, protocols)
        ],
        "algorithm": algorithms,
        "group": groups,
    }

    metrics = {}

    for variables in expand(yaml.dump(data, Dumper=yaml.SafeDumper)):
        logger.debug(variables)

        score_path = env.from_string(score_jinja_template).render(variables)
        logger.info(score_path)

        database, protocol, algorithm, group = (
            variables["evaluation"]["database"],
            variables["evaluation"]["protocol"],
            variables["algorithm"],
            variables["group"],
        )

        # if algorithm name does not have train_database name in it.
        if train_database not in algorithm and database != train_database:
            score_path = score_path.replace(algorithm, database + "_" + algorithm)
            logger.info("Score path changed to: %s", score_path)

        if not os.path.exists(score_path):
            metrics[(database, protocol, algorithm, group)] = (float("nan"),) * 5
            continue

        scores = load_score(score_path)
        neg, pos = get_negatives_positives(scores)
        (neg, pos), fta = get_fta((neg, pos))

        if group == "eval":
            threshold = metrics[(database, protocol, algorithm, "dev")][1]
        else:
            try:
                threshold = eer_threshold(neg, pos)
            except RuntimeError:
                logger.error("Something wrong with {}".format(score_path))
                raise

        far, frr = farfrr(neg, pos, threshold)
        hter = (far + frr) / 2

        metrics[(database, protocol, algorithm, group)] = (
            hter,
            threshold,
            fta,
            far,
            frr,
        )

    logger.debug("metrics: %s", metrics)

    headers = ["Algorithms"]
    for db in databases:
        headers += [db + "\nEER_t", "\nEER_d", "\nAPCER", "\nBPCER", "\nACER"]
    rows = []

    # sort the algorithms based on HTER test, EER dev, EER train
    if sort:
        train_protocol = protocols[databases.index(train_database)]

        def sort_key(alg):
            r = []
            for grp in ("eval", "dev", "train"):
                hter = metrics[(train_database, train_protocol, alg, group)][0]
                r.append(1 if math.isnan(hter) else hter)
            return tuple(r)

        algorithms = sorted(algorithms, key=sort_key)

    for algorithm in algorithms:
        name = algorithm.replace(train_database + "_", "")
        name = name.replace(train_protocol + "_", "")
        name = names.get(name, name)
        rows.append([name])
        for database, protocol in zip(databases, protocols):
            cell = []
            for group in groups:
                hter, threshold, fta, far, frr = metrics[
                    (database, protocol, algorithm, group)
                ]
                if group == "eval":
                    cell += [far, frr, hter]
                else:
                    cell += [hter]
            cell = [round(c * 100, 1) for c in cell]
            rows[-1].extend(cell)

    title = " Trained on {} ".format(train_database)
    title_line = "\n" + "=" * len(title) + "\n"
    # open log file for writing if any
    ctx.meta["log"] = (
        ctx.meta["log"] if ctx.meta["log"] is None else open(ctx.meta["log"], "w")
    )
    click.echo(title_line + title + title_line, file=ctx.meta["log"])
    click.echo(
        tabulate(rows, headers, ctx.meta["tablefmt"], floatfmt=".1f"),
        file=ctx.meta["log"],
    )
