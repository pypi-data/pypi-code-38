from typing import NamedTuple, List, Tuple

from tabulate import tabulate
from click import style
from yamlcfg import YamlConfig

from apeiron.models import Modpack
from apeiron.models import ModpackStatus
from apeiron.models import SourceManifest


class ShortModpackInfo(NamedTuple):
    id: str
    title: str
    status: str
    enabled: str


STATUS_COLOR_MAP = {
    ModpackStatus.FRESH: dict(fg="green", bold=True),
    ModpackStatus.OUTDATED: dict(fg="yellow"),
    ModpackStatus.NOT_DEPLOYED: dict(fg="green", dim=True),
    ModpackStatus.BROKEN: dict(fg="red", bold=True),
    ModpackStatus.UNKNOWN: dict(fg="black"),
    ModpackStatus.ORPHANED: dict(fg="red", dim=True),
}

ACTIVITY_COLOR_MAP = {
    True: dict(bold=True),
    False: dict(dim=True),
}


def extract_info(modpack: Modpack) -> ShortModpackInfo:
    if modpack.source_manifest is not None:
        title = modpack.source_manifest.title
    elif modpack.target_manifest is not None:
        title = modpack.target_manifest.title
    else:
        title = "???"

    return ShortModpackInfo(
        id=style(modpack.name, bold=modpack.enabled),
        title=title,
        status=style(modpack.status.value, **STATUS_COLOR_MAP[modpack.status]),
        enabled=style("Yes" if modpack.enabled else "No", **ACTIVITY_COLOR_MAP[modpack.enabled]),
    )


def print_modpacks(modpacks: List[Modpack]) -> str:
    return tabulate(
        map(extract_info, modpacks),
        headers=[style(s.capitalize(), fg='blue', bold=True) for s in ShortModpackInfo._fields],
        tablefmt="fancy_grid"
    )


def print_source_manifest(manifest: SourceManifest) -> str:
    user_files: int = len(manifest.userFiles.include)
    features: int = len(manifest.features)

    data: List[Tuple[str, str]] = [
        ("Name", style(manifest.name, fg='green')),
        ("Displayed title", style(manifest.title, fg='green')),
        ("Game version", style(manifest.gameVersion, fg='green')),
        ("Objects location", style(manifest.objectsLocation, fg='green')),
        ("User-managed files", style(f"{user_files} file(s)") if user_files else style("n/a", dim=True)),
        ("Enabled features", style(f"{features} feature(s)") if features else style("n/a", dim=True)),
    ]
    if manifest.librariesLocation is not None:
        data.append(("Libraries location", style(manifest.librariesLocation, fg='green')))

    return tabulate(data, tablefmt="fancy_grid")


def print_config(cfg: YamlConfig) -> str:
    # noinspection PyProtectedMember
    return tabulate(
        cfg._data.items(),
        headers=[style("Key", bold=True), style("Value", bold=True)],
        tablefmt="fancy_grid"
    )


def print_modpack(modpack: Modpack) -> str:
    short_info: ShortModpackInfo = extract_info(modpack)
    header = style(f"Package {short_info.id} ({short_info.title})", fg="yellow", bold=True)
    info = f"Status: {short_info.status} Enabled: {short_info.enabled}"
    source_manifest_info: str = print_source_manifest(modpack.source_manifest)
    return "\n".join((header, info, source_manifest_info))
