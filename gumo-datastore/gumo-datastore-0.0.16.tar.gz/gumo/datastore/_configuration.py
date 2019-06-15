import os
from logging import getLogger

from typing import Optional
from typing import Union

from gumo.core.injector import injector
from gumo.datastore.domain.configuration import DatastoreConfiguration


logger = getLogger('gumo.datastore')


class ConfigurationFactory:
    @classmethod
    def build(
            cls,
            use_local_emulator: Union[str, bool, None] = None,
            emulator_host: Optional[str] = None,
            namespace: Optional[str] = None,
    ) -> DatastoreConfiguration:
        _use_emulator = False
        if isinstance(use_local_emulator, bool):
            _use_emulator = use_local_emulator
        elif isinstance(use_local_emulator, str):
            _use_emulator = use_local_emulator.lower() in ['true', 'yes']

        return DatastoreConfiguration(
            use_local_emulator=_use_emulator,
            emulator_host=emulator_host,
            namespace=namespace,
        )


def configure(
        use_local_emulator: Union[str, bool, None] = None,
        emulator_host: Optional[str] = None,
        namespace: Optional[str] = None,
) -> DatastoreConfiguration:
    config = ConfigurationFactory.build(
        use_local_emulator=use_local_emulator,
        emulator_host=emulator_host,
        namespace=namespace,
    )

    if config.use_local_emulator:
        if 'DATASTORE_EMULATOR_HOST' not in os.environ:
            raise RuntimeError(
                f'The environment variable "DATASTORE_EMULATOR_HOST" is required when using a datastore emulator.'
            )
        if os.environ['DATASTORE_EMULATOR_HOST'] != config.emulator_host:
            host = os.environ['DATASTORE_EMULATOR_HOST']
            raise RuntimeError(
                f'Env-var "env["DATASTORE_EMULATOR_HOST"] and config.emulator_host are not corrected. '
                f'env["DATASTORE_EMULATOR_HOST"]={host}, config.emulator_host={config.emulator_host}'
            )

    logger.debug(f'Gumo.Datastore is configured, config={config}')

    injector.binder.bind(DatastoreConfiguration, to=config)

    from gumo.datastore._bind import datastore_binder
    injector.binder.install(datastore_binder)

    return config
