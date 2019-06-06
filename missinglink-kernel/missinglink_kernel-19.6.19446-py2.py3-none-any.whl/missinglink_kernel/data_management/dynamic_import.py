# -*- coding: utf-8 -*-
import logging
import threading

import pkg_resources
from pkg_resources import VersionConflict, DistributionNotFound, UnknownExtra

COMMON_DEPENDENCIES = [
    'ml-legit>=19.6.3709',
]

GCS_DEPENDENCIES = [
    'google-cloud-storage~=1.13',
]
S3_DEPENDENCIES = [
    'boto3~=1.9',
]

KEYWORDS = []


__pip_install_lock = threading.Lock()


def __get_non_installed_dependencies(dependencies):
    needed_dependencies = []
    for requirement in dependencies:
        if _is_dependency_installed(requirement):
            continue

        needed_dependencies += [requirement]

    return needed_dependencies


def install_dependencies(dependencies, throw_exception=True):
    from missinglink.sdk import install_package

    needed_dependencies = __get_non_installed_dependencies(dependencies)

    if not needed_dependencies:
        return

    with __pip_install_lock:
        for dependency in needed_dependencies:
            install_package(dependency, pipe_streams=False)


def _is_dependency_installed(requirement):
    try:
        pkg_resources.require(requirement)
    except (DistributionNotFound, ) as ex:
        logging.debug('DistributionNotFound when checking if %s is installed "%s"', requirement, ex)
        return False
    except (VersionConflict, ) as ex:
        if str(ex.req) != requirement:
            logging.warning('VersionConflict when checking if %s is installed "%s"', requirement, ex)

        return True
    except (IOError, UnknownExtra) as ex:
        logging.warning('Error when checking if %s is installed "%s"', requirement, ex)
        return False

    return True
