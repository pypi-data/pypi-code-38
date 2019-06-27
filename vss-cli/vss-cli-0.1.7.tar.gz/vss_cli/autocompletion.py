"""Details for the auto-completion."""
import os
from typing import Any, Dict, List, Tuple  # NOQA

from requests.exceptions import HTTPError

from vss_cli import const
from vss_cli.config import Configuration
from vss_cli.exceptions import VssError


def _init_ctx(ctx: Configuration) -> None:
    """Initialize ctx."""
    # ctx is incomplete thus need to 'hack' around it
    # see bug https://github.com/pallets/click/issues/942
    ctx.client = Configuration(tk=os.environ.get('VSS_TOKEN'))
    ctx.client.endpoint = os.environ.get('VSS_ENDPOINT', None)
    ctx.client.username = os.environ.get('VSS_USER', None)
    ctx.client.password = os.environ.get('VSS_USER_PASS', None)
    ctx.client.timeout = int(
        os.environ.get('VSS_TIMEOUT', str(const.DEFAULT_TIMEOUT))
    )
    ctx.client.config = os.environ.get('VSS_CONFIG', const.DEFAULT_CONFIG)
    # fallback to load configuration
    ctx.client.load_config()


def table_formats(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    """Table Formats."""
    _init_ctx(ctx)

    completions = [
        ("plain", "Plain tables, no pseudo-graphics to draw lines"),
        ("simple", "Simple table with --- as header/footer (default)"),
        ("github", "Github flavored Markdown table"),
        ("grid", "Formatted as Emacs 'table.el' package"),
        ("fancy_grid", "Draws a fancy grid using box-drawing characters"),
        ("pipe", "PHP Markdown Extra"),
        ("orgtbl", "org-mode table"),
        ("jira", "Atlassian Jira Markup"),
        ("presto", "Formatted as PrestoDB cli"),
        ("psql", "Formatted as Postgres psql cli"),
        ("rst", "reStructuredText"),
        ("mediawiki", "Media Wiki as used in Wikpedia"),
        ("moinmoin", "MoinMain Wiki"),
        ("youtrack", "Youtrack format"),
        ("html", "HTML Markup"),
        ("latex", "LaTeX markup, replacing special characters"),
        ("latex_raw", "LaTeX markup, no replacing of special characters"),
        (
            "latex_booktabs",
            "LaTex markup using spacing and style from `booktabs",
        ),
        ("textile", "Textile"),
        ("tsv", "Tab Separated Values"),
    ]

    completions.sort()

    return [c for c in completions if incomplete in c[0]]


def virtual_machines(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_vms()
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for vm in response:
            completions.append((vm['uuid'], vm['name']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def domains(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_domains()
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['moref'], obj['name']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def folders(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_folders(summary=1)
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['moref'], obj['path']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def networks(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_networks()
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['moref'], obj['name']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def operating_systems(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_os(show_all=True, sort='guestId,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['guestId'], obj['guestFullName']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def vss_services(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_vss_services(
            show_all=True, sort='label,desc'
        )
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((f"\"{obj['label']}\"", f"{obj['id']}"))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def isos(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_isos(show_all=True, sort='name,desc')
        response.extend(ctx.client.get_user_isos())
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['name'], obj['path']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def vm_images(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_images(show_all=True, sort='name,desc')
        response.extend(ctx.client.get_user_vm_images())
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['name'], obj['path']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def inventory_properties(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.request('/inventory/options')
        if response:
            response = response.get('data')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((obj['key'], obj['value']))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def inventory_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_inventory_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (f"{obj['id']}", f"{obj['name']} ({obj['created_on']})")
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def change_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_change_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (
                    f"{obj['id']}",
                    f"{obj['vm_uuid']} ({obj['vm_name']}) "
                    f"- {obj['attribute']}",
                )
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def export_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_export_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (f"{obj['id']}", f"{obj['vm_uuid']} ({obj['vm_name']})")
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def folder_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_folder_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (f"{obj['id']}", f"{obj['moref']} ({obj['action']})")
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def image_sync_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_image_sync_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append((f"{obj['id']}", f"{obj['type']}"))

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def snapshot_requests(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_snapshot_requests(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (f"{obj['id']}", f"{obj['vm_uuid']} ({obj['vm_name']})")
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions


def account_messages(
    ctx: Configuration, args: List, incomplete: str
) -> List[Tuple[str, str]]:
    _init_ctx(ctx)
    try:
        response = ctx.client.get_user_messages(sort='created_on,desc')
    except (HTTPError, VssError):
        response = []

    completions = []  # type: List[Tuple[str, str]]
    if response:
        for obj in response:
            completions.append(
                (f"{obj['id']}", f"{obj['kind']} ({obj['subject']})")
            )

        completions.sort()

        return [c for c in completions if incomplete in c[0]]
    return completions
