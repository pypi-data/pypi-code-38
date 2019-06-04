import logging


class LogManager:
    _DEFAULT_LOG_FORMAT = "[%(threadName)s] %(asctime)s - %(levelname)s - %(name)s - %(message)s"
    _DEFAULT_DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"

    def __init__(self,
                 kv_store):
        self._logger = logging.getLogger("LogManager")
        self._kv_store = kv_store
        logging.basicConfig(format=self._DEFAULT_LOG_FORMAT)
        self._logger.setLevel(logging.DEBUG)
        self._configure_logging(None, kv_store.get_dict(default={}))
        self._logger.setLevel(logging.INFO)
        self._kv_store.on_reload(self._configure_logging)

    def _configure_logging(self, old_config, new_config):
        self._logger.debug("BEGIN _configure_logging")

        if not old_config or not old_config == new_config:
            self._logger.debug("Configuration changed, configuring logging...")
            # Basic configuration
            basic_config = {
                "filename": new_config.get('logging_filename'),
                "filemode": new_config.get('logging_filemode'),
                "format": new_config.get('logging_format', self._DEFAULT_LOG_FORMAT),
                "datefmt": new_config.get('logging_datefmt', self._DEFAULT_DATE_FORMAT),
                "level": logging.INFO
            }
            try:
                if 'logging_level' in new_config:
                    numeric_level = getattr(logging, new_config.get('logging_level'))
                    basic_config['level'] = numeric_level
                    logging.getLogger('').setLevel(numeric_level)
                else:
                    logging.getLogger('').setLevel(logging.INFO)
            except:
                self._logger.warning("Invalid level, {1}, for root logging configuration."
                                     .format("logging_level", new_config.get('logging_level')))

            self._logger.debug("Setting base configuration to {0}"
                               .format(str(basic_config)))
            logging.basicConfig(**basic_config)

            # Specific logger configuration
            if 'logging_config' in new_config and type(new_config.get('logging_config')) is dict:
                self._logger.debug("logging_config found.")
                logging_config = new_config.get('logging_config')

                for log_name in new_config.get('logging_config'):
                    logger = logging.getLogger(log_name)
                    current_logging_config = logging_config.get(log_name)
                    self._logger.debug("Configuration for {0} is {1}.".format(log_name, str(current_logging_config)))

                    if type(current_logging_config) is str:
                        self._logger.debug("Configuring logger for {0}..."
                                           .format(log_name))
                        try:
                            numeric_level = getattr(logging, current_logging_config)
                            self._logger.debug("Configuring logging level to {0} for {1}..."
                                               .format(str(numeric_level), log_name))
                            logger.setLevel(numeric_level)
                        except:
                            self._logger.warning("Invalid level, {1}, for {0} logging configuration."
                                                 .format(log_name, current_logging_config))

            else:
                self._logger.debug("logging_config NOT found.")

        else:
            self._logger.debug("Configuration unchanged.")
        self._logger.debug("END _configure_logging")
