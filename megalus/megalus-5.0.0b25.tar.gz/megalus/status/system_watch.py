"""Get machine info data.

Uses PSUtil to get machine stats:
* CPU Percent
* Free Memory
* Memory Used
"""
import psutil
from buzio import formatStr
from dashing import dashing
from dashing.dashing import Text, VSplit

from megalus import __version__
from megalus.main import Megalus


def megalus_info_widget(meg: Megalus) -> VSplit:
    """Return Megalus Info Widget.

    :return: dashing VSplit instance
    """
    machine_info_widget = get_machine_info_widget()
    info_widget = get_megalus_info_widget(meg)
    return VSplit(info_widget, machine_info_widget)


def get_megalus_info_widget(meg: Megalus) -> Text:
    """Get projects in error.

    :param meg: Megalus instance
    :return: String
    """
    projects_in_error = [
        project
        for project in meg.config_data['compose_projects'].keys()
        if project not in meg.all_composes
    ]
    status_text = formatStr.success("All projects loaded.",
                                    use_prefix=False) if not projects_in_error else formatStr.error(
        "Projects in error: {}".format(",".join(projects_in_error)), use_prefix=False)
    return Text(status_text, color=6, border_color=5, background_color=16,
                title="Megalus v{}".format(__version__))


def get_machine_info_widget() -> VSplit:
    """Return widget from machine stats.

    :return: dashing.HSplit
    """
    cpu_percent = round(psutil.cpu_percent(interval=None) * 10, 0) / 10
    free_memory = int(psutil.virtual_memory().available / 1024 / 1024)
    total_memory = int(psutil.virtual_memory().total / 1024 / 1024)
    memory_percent = (free_memory / total_memory) * 100
    free_space = round(psutil.disk_usage("/").free / 1024 / 1024 / 1024, 1)
    total_space = round(psutil.disk_usage(
        "/").total / 1024 / 1024 / 1024, 1)
    space_percent = (free_space / total_space) * 100

    if memory_percent > 100:
        memory_percent = 100

    if space_percent > 100:
        space_percent = 100

    if cpu_percent <= 50:
        cpu_color = 2
    elif cpu_percent <= 70:
        cpu_color = 3
    else:
        cpu_color = 1

    if memory_percent <= 20:
        memory_color = 1
    elif memory_percent <= 50:
        memory_color = 3
    else:
        memory_color = 2

    if space_percent <= 20:
        space_color = 1
    elif space_percent <= 50:
        space_color = 3
    else:
        space_color = 2

    return dashing.VSplit(
        dashing.HSplit(
            dashing.HGauge(
                val=cpu_percent,
                color=cpu_color,
                border_color=cpu_color,
                title="CPU:{}%".format(cpu_percent),
                background_color=16
            ),
            dashing.HGauge(
                val=memory_percent,
                color=memory_color,
                border_color=memory_color,
                title="Free Mem:{}M".format(free_memory),
                background_color=16
            ),
        ),
        dashing.HGauge(
            val=space_percent,
            color=space_color,
            border_color=space_color,
            title="Free Space:{}Gb".format(free_space),
            background_color=16
        )
    )
