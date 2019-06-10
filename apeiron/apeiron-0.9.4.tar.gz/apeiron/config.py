from os import environ

from pathlib import Path

from yamlcfg import YAMLConfig


cfg = YAMLConfig(
    paths=[
        Path(environ.get('APEIRON_CONFIG', '~/.config/apeiron.yaml')).expanduser().as_posix()
    ],
    permute=False
)

DEFAULTS = dict(
    storage_dir=Path('~/apeiron/storage').expanduser().as_posix(),
    modpack_index="index.json",
    parallelism=12,
)
