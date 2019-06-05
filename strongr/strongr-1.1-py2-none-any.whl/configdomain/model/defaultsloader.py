class DefaultsLoader:
    def getConfig(self):
        return {
            'internal': {
                'configloaderorder': ['IniLoader', 'JsonLoader', 'YamlLoader']
            },
            'cache': {
                'driver': 'local',
                'namespace': 'strongr-cache-'
            },
            'lock': {
                'driver': 'local',
                'redis': {
                    'timeout': 10,
                    'namespace': 'strongr-redislock-'
                },
                'file': {
                    'timeout': 10,
                    'path': '/var/lock/strongr'
                }
            },
            'db': {
                'engine': {
                    'url': 'sqlite:////tmp/strongr.db',
                    'echo': True
                }
            },
            'stats': {
                'driver': "null"
            },
            'clouddomain': {
                'driver': 'MockCloud',
                'OpenNebula': {
                    'salt_config': '/etc/salt'
                },
                'MockCloud': {
                    'scratch': '/tmp/strongr_mockcloud_scratch'
                }
            },
            'restdomain': {
                'backend': 'flask',
                'flask': {
                    'host': '127.0.0.1',
                    'port': 8080,
                    'debug': True
                },
                "gunicorn": {
                    "bind": "0.0.0.0:8080",
                    "worker_class": "sync"
                }
            },
            'schedulerdomain': {
                'scalingdriver': 'nullscaler',
                'simplescaler': {
                    'scaleoutmincoresneeded': 1,
                    'scaleoutminramneeded': 1
                }
            },
            'logger': {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                    }
                },
                'handlers': {
                    'default': {
                        'level': 'INFO',
                        'formatter': 'standard',
                        'class': 'logging.StreamHandler'
                    }
                },
                'loggers': {
                    '': {
                        'handlers': [
                            'default'
                        ],
                        'level': 'INFO',
                        'propagate': True
                    }
                }
            }
        }
