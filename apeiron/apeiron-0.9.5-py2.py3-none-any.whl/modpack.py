from itertools import chain
from pathlib import Path
from typing import Optional, List, Set

from apeiron import manifest
from apeiron.config import cfg
from apeiron import constants as c
from apeiron import exceptions as exc
from apeiron import models as m


def infer_modpack_status(source_manifest: m.SourceManifest, target_manifest: m.TargetManifest) -> m.ModpackStatus:
    if source_manifest is not None:
        if target_manifest is not None:
            if not manifest.validate_target_manifest(target_manifest):
                return m.ModpackStatus.BROKEN
            if manifest.build_target_manifest(source_manifest) == target_manifest:
                return m.ModpackStatus.FRESH
            else:
                return m.ModpackStatus.OUTDATED
        else:
            return m.ModpackStatus.NOT_DEPLOYED
    else:
        if target_manifest is not None:
            return m.ModpackStatus.ORPHANED
        else:
            return m.ModpackStatus.UNKNOWN


def get_modpack(package_id: str) -> m.Modpack:
    source_manifest: Optional[m.SourceManifest] = manifest.load_source_manifest(package_id)
    target_manifest: Optional[m.TargetManifest] = manifest.load_target_manifest(package_id)
    status: m.ModpackStatus = infer_modpack_status(source_manifest, target_manifest)
    manifest_info: m.ManifestInfo = manifest.get_manifest_info(source_manifest, target_manifest)

    return m.Modpack(
        name=package_id,
        status=status,
        enabled=manifest_info in manifest.get_enabled_manifests().packages,
        source_manifest=source_manifest,
        target_manifest=target_manifest,
    )


def get_modpacks() -> List[m.Modpack]:
    fs_modpack_ids: Set[str] = {
        d.name for d in
        chain(
            (Path(cfg.storage_dir) / Path(c.PACKAGES_DIR)).iterdir(),
            (Path(cfg.storage_dir) / Path(c.SOURCES_DIR)).iterdir(),
        )
        if d.is_dir()
    }

    enabled_modpacks_ids: Set[str] = {
        manifest_info.name
        for manifest_info
        in manifest.get_enabled_manifests().packages
    }

    return list(map(get_modpack, sorted(fs_modpack_ids | enabled_modpacks_ids)))


def enable_modpack(package_id: str):
    modpack: m.Modpack = get_modpack(package_id)

    if modpack.enabled:
        raise exc.StateConflictError(f"Modpack «{modpack.name}» already enabled!")

    if modpack.status not in {m.ModpackStatus.FRESH, m.ModpackStatus.OUTDATED}:
        raise exc.InvalidStatusError(
            f"Only «{m.ModpackStatus.FRESH.value}» and «{m.ModpackStatus.OUTDATED.value}» "
            f"can be enabled, but modpack «{modpack.name}» is «{modpack.status.value}»"
        )

    manifest_info: m.ManifestInfo = manifest.get_manifest_info(modpack.source_manifest, modpack.target_manifest)
    manifest_index: m.ManifestIndex = m.ManifestIndex(
        packages=[manifest_info, *manifest.get_enabled_manifests().packages]
    )

    manifest.save_manifests(manifest_index)


def disable_modpack(package_id: str):
    modpack: m.Modpack = get_modpack(package_id)

    if not modpack.enabled:
        raise exc.StateConflictError(f"Modpack «{modpack.name}» already disabled!")

    manifest_index: m.ManifestIndex = m.ManifestIndex(packages=[
        manifest_info
        for manifest_info
        in manifest.get_enabled_manifests().packages
        if manifest_info.name != package_id
    ])

    manifest.save_manifests(manifest_index)


def delete_modpack(package_id: str, prune: bool = False) -> List[exc.ManifestError]:
    modpack: m.Modpack = get_modpack(package_id)
    warnings: List[exc.ManifestError] = []

    if modpack.enabled:
        raise exc.StateConflictError(f"Can't delete modpack «{modpack.name}», because it's enabled!")

    if modpack.target_manifest is None:
        warnings.append(exc.ConsistenceError(f"There are no built files for «{modpack.name}», suppressing…"))
    else:
        manifest.delete_target_manifest(modpack.target_manifest)

    if prune:
        if modpack.source_manifest is None:
            warnings.append(exc.ConsistenceError(f"There are no sources for «{modpack.name}», suppressing…"))
        else:
            manifest.delete_source_manifest(modpack.source_manifest)

    return warnings


def build_modpack(package_id: str, strict: bool, debug: bool):
    modpack: m.Modpack = get_modpack(package_id)
    allowed_statuses: Set[m.ModpackStatus] = {
        m.ModpackStatus.FRESH,
        m.ModpackStatus.OUTDATED,
        m.ModpackStatus.NOT_DEPLOYED,
        m.ModpackStatus.BROKEN,
    }

    if modpack.status not in allowed_statuses:
        statuses = ', '.join(s.value for s in allowed_statuses)
        raise exc.InvalidStatusError(
            f"Only {statuses} allowed to build! "
            f"Modpack «{modpack.name}» is {modpack.status.value} and should be only deleted."
        )

    built_manifest: m.TargetManifest = manifest.build_target_manifest(modpack.source_manifest)

    manifest.cleanup_target_location(built_manifest.name, built_manifest.objectsLocation, strict)
    manifest.save_target_manifest(built_manifest)
    manifest.save_target_content(modpack.source_manifest, built_manifest, debug)
