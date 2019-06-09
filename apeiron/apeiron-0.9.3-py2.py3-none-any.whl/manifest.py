import json
from typing import Optional, Dict, Union, List, Any, Iterable

import yaml
import uuid
from shutil import rmtree
from shutil import copy
from functools import partial
from multiprocessing import cpu_count
from multiprocessing import Pool
from hashlib import sha1
from pathlib import Path

import click
from pydantic import ValidationError

from apeiron import constants as c
from apeiron import models as m
from apeiron.config import cfg
from apeiron.exceptions import ManifestError


def validate_manifest_fs(package_id: str, manifest: m.RichManifest) -> bool:
    consistent = manifest.name == package_id
    if not consistent:
        click.echo(click.style(
            f"Inconsistent {manifest.__class__.__name__}! "
            f"Internal id equals «{manifest.name}», but resides in «{package_id}»!",
            fg='red',
            bold=True
        ))
    return consistent


def load_target_manifest(package_id: str) -> Optional[m.TargetManifest]:
    path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / package_id / c.TARGET_MANIFEST_INDEX

    if not path.exists():
        return None

    try:
        manifest = m.TargetManifest(**json.load(path.open()))
    except ValidationError as e:
        click.echo(click.style(f"Broken TargetManifest, id: «{package_id}». Reason: {str(e)}", fg='red'))
        return None
    else:
        return validate_manifest_fs(package_id, manifest) and manifest or None


def _validate_task(path: Path, task: m.Task) -> bool:
    return (path / task.location).exists()


def validate_target_manifest(manifest: m.TargetManifest) -> bool:
    path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / manifest.name / manifest.objectsLocation

    if not path.exists():
        return False

    with Pool(processes=cfg.parallelism or cpu_count()) as pool:
        return all(pool.imap_unordered(partial(_validate_task, path), manifest.tasks))


def delete_target_manifest(manifest: m.TargetManifest):
    path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / manifest.name
    rmtree(path.as_posix())


def load_source_manifest(package_id: str) -> Optional[m.SourceManifest]:
    path: Path = Path(cfg.storage_dir) / c.SOURCES_DIR / package_id / c.SOURCE_MANIFEST_INDEX

    if not path.exists():
        return None

    try:
        manifest = m.SourceManifest(**yaml.load(path.open()))
    except ValidationError as e:
        click.echo(click.style(f"Broken SourceManifest, id: «{package_id}». Reason: {str(e)}", fg='red'))
        return None
    else:
        return validate_manifest_fs(package_id, manifest) and manifest or None


def delete_source_manifest(manifest: m.SourceManifest):
    path: Path = Path(cfg.storage_dir) / c.SOURCES_DIR / manifest.name
    rmtree(path.as_posix())


def _generate_task(
    user_files: m.PatternTestable,
    features: Dict[str, m.PatternTestable],
    base_dir: Path,
    path: Path,
) -> Union[m.Task, m.UserFileTask, m.FeatureTask]:
    with path.open(mode='rb') as file:
        data: str = file.read()
        digest: str = sha1(data).hexdigest()
        destination: str = path.relative_to(base_dir).as_posix()
        affected_features: List[str] = [
            name
            for name, feature_pattern
            in features.items()
            if destination in feature_pattern
        ]
        base_data: Dict[str, Union[str, int]] = dict(
            hash=digest,
            location="{}/{}/{}".format(digest[0:2], digest[2:4], digest),
            to=destination,
            size=len(data)
         )
        if affected_features:
            return m.FeatureTask(
                when={"if": "requireAny", "features": affected_features},
                **base_data
            )
        elif destination in user_files:
            return m.UserFileTask(**base_data)
        else:
            return m.Task(**base_data)


def build_target_manifest(source: m.SourceManifest) -> m.TargetManifest:
    user_files: m.PatternTestable = m.PatternTestable(source.userFiles.include)
    features: Dict[str, m.PatternTestable] = {
        f.properties.name: m.PatternTestable(f.files.include)
        for f
        in source.features
    }

    path: Path = Path(cfg.storage_dir) / c.SOURCES_DIR / source.name / source.objectsLocation
    raw_files: List[Path] = [path for path in path.glob('**/*') if path.is_file()]
    target_features: List[m.FeatureProperties] = [f.properties for f in source.features]
    common_values: Dict[str, Any] = source.dict(include=m.RichManifest.construct().fields)

    with Pool(processes=cfg.parallelism or cpu_count()) as pool:
        tasks: Iterable[Union[m.Task, m.FeatureTask, m.UserFileTask]] = pool.imap_unordered(
            partial(_generate_task, user_files, features, path),
            raw_files
        )
        return m.TargetManifest(features=target_features, tasks=tasks, **common_values)


def cleanup_target_location(manifest_name: str, objects_dir: str, strict: bool):
    base_path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / manifest_name

    if strict and base_path.exists():
        raise ManifestError(f"Base path {base_path} for modpack {manifest_name} already exists!")

    try:
        rmtree(base_path.as_posix())
    except FileNotFoundError as e:
        click.echo(click.style(f"Target {base_path.as_posix()} doesn't exist, suppressing…", fg="yellow", bold=True))
    except IOError as e:
        raise ManifestError(f"Can't clean target dir: {str(e)}") from e
    else:
        click.echo(f"Removed {click.style(base_path.as_posix(), bold=True)} (due to disabled strict mode)")

    try:
        base_path.mkdir()
        (base_path / objects_dir).mkdir()
    except IOError as e:
        raise ManifestError(f"Can't create target directory: {str(e)}") from e
    else:
        click.echo(f"Created empty directory: {click.style(base_path.as_posix(), bold=True)}")


def save_target_manifest(manifest: m.TargetManifest):
    base_path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / manifest.name
    index_path: Path = base_path / c.TARGET_MANIFEST_INDEX

    try:
        json.dump(manifest.dict(), index_path.open("w", encoding="utf-8"), indent=2, ensure_ascii=False)
    except (IOError, ValueError, TypeError, json.decoder.JSONDecodeError) as e:
        raise ManifestError(f"Can't write target index: {str(e)}") from e
    else:
        click.echo(f"Wrote target index at: {click.style(index_path.as_posix(), bold=True)}")


def _save_target_task(
    source_base_path: Path,
    target_base_path: Path,
    debug: bool,
    task: Union[m.Task, m.UserFileTask, m.FeatureTask]
) -> bool:
    target: Path = target_base_path / task.location
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        copy(
            (source_base_path / task.to).as_posix(),
            (target_base_path / task.location).as_posix()
        )
    except IOError:
        return False
    else:
        return True
    finally:
        if debug:
            click.echo(click.style(f"Copying: {task.location} ← {task.to}", dim=True))


def save_target_content(source_manifest: m.SourceManifest, target_manifest: m.TargetManifest, debug: bool):
    source_path: Path = Path(cfg.storage_dir) / c.SOURCES_DIR / source_manifest.name / source_manifest.objectsLocation
    target_path: Path = Path(cfg.storage_dir) / c.PACKAGES_DIR / target_manifest.name / target_manifest.objectsLocation

    with Pool(processes=cfg.parallelism or cpu_count()) as pool:
        tasks: Iterable[bool] = pool.map(
            partial(_save_target_task, source_path, target_path, debug),
            target_manifest.tasks
        )
        result = all(tasks)

    if result:
        click.echo(click.style(f"Deployed {len(target_manifest.tasks)} files"))
    else:
        raise ManifestError("Error happened while copying target files")


def get_manifest_index_path() -> Path:
    return Path(cfg.storage_dir) / c.PACKAGES_DIR / cfg.modpack_index


def get_enabled_manifests() -> m.ManifestIndex:
    return m.ManifestIndex(**json.load(get_manifest_index_path().open()))


def save_manifests(modpack_index: m.ManifestIndex):
    with get_manifest_index_path().open('w') as file_handler:
        json.dump(modpack_index.dict(), file_handler, ensure_ascii=False, indent=2)


def get_manifest_info(
    source_manifest: Optional[m.SourceManifest],
    target_manifest: Optional[m.TargetManifest]
) -> m.ManifestInfo:
    if source_manifest is not None:
        location = Path(source_manifest.name) / c.TARGET_MANIFEST_INDEX
        name = source_manifest.name
        title = source_manifest.title
        version = source_manifest.version
    elif target_manifest is not None:
        location = Path(target_manifest.name) / c.TARGET_MANIFEST_INDEX
        name = target_manifest.name
        title = target_manifest.title
        version = target_manifest.version
    else:
        name = "unknown_" + uuid.uuid4().hex
        title = "unknown_" + uuid.uuid4().hex
        version = "0.0"
        location = Path("/tmp") / uuid.uuid4().hex

    return m.ManifestInfo(
        name=name,
        title=title,
        version=version,
        location=location.as_posix(),
    )


def bootstrap_source_manifest(manifest: m.SourceManifest) -> Path:
    base_path: Path = Path(cfg.storage_dir) / c.SOURCES_DIR / manifest.name

    if base_path.exists():
        raise ManifestError(f"Base path {base_path} for modpack {manifest.name} already exists!")

    base_path.mkdir()
    (base_path / manifest.objectsLocation).mkdir()

    index_path: Path = base_path / c.SOURCE_MANIFEST_INDEX

    yaml.dump(
        manifest.dict(),
        index_path.open("w", encoding="utf-8"),
        encoding="utf-8",
        indent=2,
    )

    return index_path
