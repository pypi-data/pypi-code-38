from guillotina import testing


def settings_configurator(settings):
    if 'applications' in settings:
        settings['applications'].append('guillotina_batch')
    else:
        settings['applications'] = ['guillotina_batch']


testing.configure_with(settings_configurator)
