#!/usr/bin/env python3

# We are going to load data from a file. If this package is installed,
# it needs to be able to find the file properly
import pkg_resources
import re


# Data files are to be newline delimited lists, space separated
def load_device_name_data_from_file(path):
    file_stream = pkg_resources.resource_string(__name__, path)
    data = filter(bool, file_stream.decode('utf-8').split('\n'))
    device_name_dictionary = {}
    for datapoint in data:
        split = datapoint.split(' ')
        common_name = split[0]
        numeric_name = split[1]
        device_name_dictionary[common_name] = numeric_name
    return device_name_dictionary


def load_device_major_minor_data_from_file(path):
    file_stream = pkg_resources.resource_string(__name__, path)
    data = filter(bool, file_stream.decode('utf-8').split('\n'))
    device_major_minor_dictionary = {}
    for datapoint in data:
        split = datapoint.split(' ')
        common_name = split[0]
        numeric_name = split[1]
        device_major_minor_dictionary[numeric_name] = common_name
    return device_major_minor_dictionary


# TODO: Make these support multiple data paths
def construct_name_hash_lookup(data_paths):
    linux_allocated_devices = {
        'scsi_disk_devices': load_device_name_data_from_file(data_paths)
    }
    return linux_allocated_devices


def construct_major_minor_hash_lookup(data_paths):
    linux_allocated_devices = {
        'scsi_disk_devices': load_device_major_minor_data_from_file(data_paths)
    }
    return linux_allocated_devices


def convert(string):
    if re.search('^[a-z]{2,4}[0-9]{1,3}', string.lower()):
        lookup_table = construct_name_hash_lookup('data/scsi_disk_devices.txt')
        return lookup_table['scsi_disk_devices'][string]
    elif re.search('^[0-9]{1,3}:[0-9]{1,3}', string.lower()):
        lookup_table = construct_major_minor_hash_lookup(
            'data/scsi_disk_devices.txt')
        return lookup_table['scsi_disk_devices'][string]
    else:
        raise NotImplementedError(
            f'Chosen device f{string} is either not implemented or has no known matching LAD'
        )
