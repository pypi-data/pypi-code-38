# -*- coding: utf-8 -*-
import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils import HiddenOption, tabulate_rows, prettify_size, with_emoji
from spell.cli.log import logger

# display order of CPU columns
CPU_COLUMNS = [
    "cpu_percentage",
    "memory_percentage",
    "mem_ratio",
    "net_ratio",
    "block_ratio",
]

# title lookup
CPU_TITLES = {
    "cpu_percentage": "CPU %",
    "memory_percentage": "MEM %",
    "mem_ratio": "MEM Usage / MEM Total",
    "net_ratio": "Network I/O",
    "block_ratio": "Block I/O"
}

# display order of GPU columns
GPU_COLUMNS = [
    "name",
    "temperature",
    "perf_state",
    "power_ratio",
    "mem_ratio",
    "memory_utilization",
    "gpu_utilization"
]

# title lookup
GPU_TITLES = {
    "name": "GPU Name",
    "temperature": "Temperature",
    "perf_state": "Performance State",
    "power_ratio": "PWR Usage / PWR Limit",
    "mem_ratio": "MEM Usage / MEM Total",
    "memory_utilization": "MEM %",
    "gpu_utilization": "GPU %"
}


@click.command(name="stats",
               short_help="Display performance statistics for a run")
@click.argument("run_id")
@click.option("--raw", help="Display output in raw format.", is_flag=True, default=False, cls=HiddenOption)
@click.option("-f", "--follow", is_flag=True, help="Continually stream stats for the run")
@click.pass_context
def stats(ctx, run_id, raw, follow):
    """
    Display performance statistics for a run specified by RUN_ID

    A run must have status 'Running' to display performance statistics. CPU statistics (e.g., memory usage,
    CPU utilization) and, if applicable for the machine type, GPU statistics (e.g., power and GPU memory utilization)
    are displayed.
    """
    client = ctx.obj["client"]

    with api_client_exception_handler():
        logger.info("Retrieving stats from Spell")
        try:
            for (cpu_stats, gpu_stats) in client.get_stats(run_id, follow=follow):
                print_stats(run_id, cpu_stats, gpu_stats, raw=raw, clear=follow)
            if follow:
                click.echo("Run {} is no longer running".format(run_id))
        except KeyboardInterrupt:
            msg = "Use 'spell stats {} {}' to view stats again".format("--follow" if follow else "", run_id)
            click.echo(with_emoji(u"✨", msg, ctx.obj["utf8"]))


def print_stats(run_id, cpu_stats, gpu_stats, raw=False, clear=False):
    if clear:
        click.echo("\033[2J")
        click.echo("\033[H", nl=False)
    if raw:
        click.echo("\n".join(["{},{}".format(x, y) for x, y in [val for val in cpu_stats.__dict__.items()]]))
        if gpu_stats:
            click.echo("\n".join(["{},{}".format(x, y) for x, y in [val for val in gpu_stats.__dict__.items()]]))
    else:
        click.echo("CPU statistics for run {}:".format(run_id))
        cpu_stats.cpu_percentage = "{:.2f}%".format(cpu_stats.cpu_percentage)
        cpu_stats.memory_percentage = "{:.2f}%".format(cpu_stats.memory_percentage)
        cpu_stats.mem_ratio = "{} / {}".format(prettify_size(cpu_stats.memory),
                                               prettify_size(cpu_stats.memory_total))
        cpu_stats.net_ratio = "{} / {}".format(prettify_size(cpu_stats.network_rx),
                                               prettify_size(cpu_stats.network_tx))
        cpu_stats.block_ratio = "{} / {}".format(prettify_size(cpu_stats.block_read),
                                                 prettify_size(cpu_stats.block_write))
        tabulate_rows([cpu_stats], headers=[CPU_TITLES[col] for col in CPU_COLUMNS], columns=CPU_COLUMNS)
        if gpu_stats:
            click.echo()
            click.echo("GPU statistics for run {}:".format(run_id))
            for row in gpu_stats:
                row.power_ratio = "{} / {}".format(row.power_draw, row.power_limit)
                row.mem_ratio = "{} / {}".format(row.memory_used, row.memory_total)
            tabulate_rows(gpu_stats, headers=[GPU_TITLES[col] for col in GPU_COLUMNS], columns=GPU_COLUMNS)
