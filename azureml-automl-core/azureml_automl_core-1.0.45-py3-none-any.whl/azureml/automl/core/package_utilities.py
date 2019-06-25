# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common utilities related to package discovery and version checks."""
from typing import Any, Dict, Optional, Set, Tuple
import logging
import pkg_resources


def _all_dependencies() -> Dict[str, str]:
    """
    Retrieve the packages from the site-packages folder by using pkg_resources.

    :return: A dict contains packages and their corresponding versions.
    """
    dependencies_versions = dict()
    for d in pkg_resources.working_set:
        dependencies_versions[d.key] = d.version
    return dependencies_versions


def _is_sdk_package(name: str) -> bool:
    """Check if a package is in sdk by checking the whether the package startswith('azureml')."""
    return name.startswith('azureml')


def get_sdk_dependencies(
    all_dependencies_versions: Optional[Dict[str, str]] = None,
    logger: Optional[logging.Logger] = None,
    **kwargs: Dict[Any, Any]
) -> Dict[str, str]:
    """
    Return the package-version dict.

    :param all_dependencies_versions:
        If None, then get all and filter only the sdk ones.
        Else, only check within the that dict the sdk ones.
    :param logger: The logger.
    :return: The package-version dict.
    """
    sdk_dependencies_version = dict()
    if all_dependencies_versions is None:
        all_dependencies_versions = _all_dependencies()
    for d in all_dependencies_versions:
        if _is_sdk_package(d):
            sdk_dependencies_version[d] = all_dependencies_versions[d]

    return sdk_dependencies_version


def _check_dependencies_versions(
    old_versions: Dict[str, str],
    new_versions: Dict[str, str]
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """
    Check the SDK packages between the training environment and the predict environment.

    Then it gives out 2 kinds of warning combining sdk/not sdk with missing or version mismatch.

    :param old_versions: Packages in the training environment.
    :param new_versions: Packages in the predict environment.
    :return: sdk_dependencies_mismatch, sdk_dependencies_missing,
             other_depencies_mismatch, other_depencies_missing
    """
    sdk_dependencies_mismatch = set()
    other_depencies_mismatch = set()
    sdk_dependencies_missing = set()
    other_depencies_missing = set()

    for d in old_versions.keys():
        if d in new_versions and old_versions[d] != new_versions[d]:
            if _is_sdk_package(d):
                sdk_dependencies_mismatch.add(d)
            else:
                other_depencies_mismatch.add(d)
        elif d not in new_versions:
            if _is_sdk_package(d):
                sdk_dependencies_missing.add(d)
            else:
                other_depencies_missing.add(d)

    return sdk_dependencies_mismatch, sdk_dependencies_missing, \
        other_depencies_mismatch, other_depencies_missing


def _has_version_discrepancies(sdk_dependencies: Dict[str, str]) -> bool:
    """
    Check if the sdk dependencies are different from the current environment.

    Returns true is there are discrepancies false otherwise.
    """
    current_dependencies = _all_dependencies()
    sdk_mismatch, sdk_missing, other_mismatch, other_missing = _check_dependencies_versions(
        sdk_dependencies, current_dependencies
    )

    if len(sdk_mismatch) == 0 and len(sdk_missing) == 0:
        logging.info('No issues found in the SDK package versions.')
        return False

    if len(sdk_mismatch) > 0:
        logging.warning('The version of the SDK does not match the version the model was trained on.')
        logging.warning('The consistency in the result may not be guaranteed.')
        message_template = 'Package:{}, training version:{}, current version:{}'
        message = []
        for d in sorted(sdk_mismatch):
            message.append(message_template.format(d, sdk_dependencies[d], current_dependencies[d]))
        logging.warning('\n'.join(message))

    if len(sdk_missing) > 0:
        logging.warning('Below packages were used for model training but missing in current environment:')
        message_template = 'Package:{}, training version:{}'
        message = []
        for d in sorted(sdk_missing):
            message.append(message_template.format(d, sdk_dependencies[d]))
        logging.warning('\n'.join(message))

    return True
