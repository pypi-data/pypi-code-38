import json

import logging

recognized_types = {
    'container', 'string', 'integer', 'decimal', 'single_choice', 'multiple_choice', 'checkbox',
}

non_supported_types = {
    'subject', 'file'
}


def parse_tool_settings(settings_path, settings_values_path):
    """
    Parse tool settings and their values

    Parameters
    ----------
    settings_path : str
        Path to the settings file. Uses JSON format and same syntax as platform.
    settings_values_path : str
        Path to the settings' values file. Uses JSON format.

    Returns
    -------
    dict
        Dictionary with key-value settings
    """
    logger = logging.getLogger(__name__)

    settings_description = None
    with open(settings_path, 'r') as fd:
        try:
            settings_description = json.load(fd)
        except ValueError:
            raise SettingsException('{} does not have a proper JSON format'.format(settings_path))

    input_settings = None
    with open(settings_values_path, 'r') as fd:
        try:
            input_settings = json.load(fd)
        except ValueError:
            raise InputSettingsException('{} does not have a proper JSON format'.format(settings_values_path))

    out_dict = dict()
    for elem in settings_description:
        setting_type = elem['type']
        if setting_type in non_supported_types:
            logger.warning("The setting type {} is not supported".format(setting_type))
            continue
        elif setting_type in recognized_types:
            setting_id = elem['id']
            mandatory = elem.get('mandatory', False)  # Assume mandatory is False if not set --> optional is True
            if setting_id in input_settings:
                out_dict[setting_id] = input_settings[setting_id]
            elif 'default' in elem:
                out_dict[setting_id] = elem['default']
            elif mandatory:
                raise InputSettingsException('Setting with id {} requires a value of type {}'.format(
                    setting_id, setting_type)
                )

    return out_dict


class SettingsException(Exception):
    pass


class InputSettingsException(Exception):
    pass
