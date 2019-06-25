import sys
import logging

import honey_board.modules.operation_timing_modules.operation_timing as operation_timing
import honey_board.modules.shell_starter_modules.shell_starter_module as shell_starter
import honey_board.models.settings.config as config
#init system configs, settings, etc.
def init_system():
    try:
        #init config
        config.init_config()

    except Exception as e:
        logging.error("Error. "+str(e))

#entry point project
if __name__ == '__main__':
    try:
        start_time = operation_timing.get_start_time()
        init_system()
        args_count =len(sys.argv)
        if (args_count>1):
            shell_starter.cli()

        operation_timing.print_execution_time(start_time, "All operations completed.")
    except Exception as e:
        logging.error("Error. "+str(e))