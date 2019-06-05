from pkg_resources import require
require('pygelf>=0.3.1')
require("numpy>=1.11.1")
require("scipy>=0.19.1")

import logging
import logging.handlers
import time
import os

from CrystalMatch.dls_imagematch.service.parser_manager import ParserManager
from CrystalMatch.dls_imagematch.service.service import CrystalMatch
from CrystalMatch.dls_imagematch import logconfig

class CrystalMatchService:

    def __init__(self):
       pass

    def run(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        try:
            total_start = time.time()
            parser_manager = ParserManager()
            script_path = os.path.dirname(os.path.abspath(__file__))
            parser_manager.set_script_path(script_path)
            parser_manager.build_parser()

            logconfig.set_additional_handler(parser_manager.get_log_file_path())

            config_directory = parser_manager.get_config_dir()

            log.info('used config directory: '+ config_directory +', path to script: '+ script_path)

            scale_override = parser_manager.get_scale_override()
            to_json_flag = parser_manager.get_to_json()

            service = CrystalMatch(config_directory, scale_override=scale_override)
            service_results = service.perform_match(parser_manager)

            total_time = time.time() - total_start
            service_results.log_final_result(total_time)
            service_results.print_results(to_json_flag)

        except IOError as e:

            log.error(e)

def main():
    logconfig.setup_logging()
    service = CrystalMatchService()
    service.run()

if __name__ == '__main__':
    main()