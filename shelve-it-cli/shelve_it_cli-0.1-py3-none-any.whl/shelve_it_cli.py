from shelve_it_cli import ArchivesSpace
from pathlib import Path
from time import sleep
import csv
import fire
import yaml


class ShelveItCLI(object):
    """Assigning containers to locations in ArchivesSpace."""

    def __init__(self):
        self.service = ArchivesSpace()

    def ping(self, config):
        print('Attempting to login to ArchivesSpace')
        self.service.config = self.__read_config(config)
        self.service.reset_client()
        self.service.ping()

    def process(self, data, config, output):
        self.service.config = self.__read_config(config)
        self.service.reset_client()
        self.__check_file(data)
        with open(data, mode='r') as dt:
            csv_reader = csv.DictReader(dt)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    pass
                line_count += 1
                rc = row["repo_code"]
                cb = row["container_barcode"]
                lb = row["location_barcode"]
                print(f'Processing: [{rc}], [{cb}], [{lb}]')
                self.service.handle(line_count, rc, cb, lb)
                sleep(0.05)
        self.__process_results(output)
        return None

    def __check_file(self, file):
        Path(file).resolve(strict=True)

    def __process_results(self, output):
        keys = self.service.results[0].keys()
        with open(output, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.service.results)

    def __read_config(self, config):
        self.__check_file(config)
        with open(config, 'r') as cfg:
            parsed_cfg = yaml.load(cfg)
        return {
            'baseurl':  parsed_cfg['base_url'],
            'username': parsed_cfg['username'],
            'password': parsed_cfg['password']
        }
