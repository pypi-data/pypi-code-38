import os
import os.path


def test_config_file():
    #import ..configure_model

    print('Create config file when it does not exist')
    configfile = os.path.join(os.environ['HOME'], '.nexoclom')
    if os.path.isfile(configfile):
        os.remove(configfile)
    print(configure_model.config_file())
    print('-'*10)
    print()

    print('Read existing config file')
    print(configure_model.config_file())
    print('-'*10)
    print()

    print('Change existing config file')
    print(configure_model.config_file(setconfig=True))
