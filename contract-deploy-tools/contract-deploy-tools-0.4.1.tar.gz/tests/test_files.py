import pytest
import csv

from eth_utils import to_checksum_address
from deploy_tools.files import read_addresses_in_csv, InvalidAddressException


@pytest.fixture()
def address_list():
    def create_address_string(i: int):
        return f"0x{str(i).rjust(40, '0')}"

    return [create_address_string(i) for i in range(30)]


@pytest.fixture()
def address_list_csv_path(tmp_path, address_list):
    folder = tmp_path / "subfolder"
    folder.mkdir()
    file_path = folder / "address.csv"

    with file_path.open("w") as f:
        writer = csv.writer(f)
        writer.writerows([[to_checksum_address(address)] for address in address_list])

    return file_path


@pytest.fixture()
def incorrect_list_csv_path(tmp_path, address_list):
    folder = tmp_path / "subfolder"
    folder.mkdir()
    file_path = folder / "incorrect.csv"
    incorrect_value = "0x123456789"

    with file_path.open("w") as f:
        writer = csv.writer(f)
        writer.writerows([[to_checksum_address(address)] for address in address_list])
        writer.writerow(incorrect_value)

    return file_path


def test_read_addresses_in_csv(address_list_csv_path, address_list):
    addresses = read_addresses_in_csv(address_list_csv_path)

    assert addresses == address_list


def test_read_incorrect_addresses_in_csv(incorrect_list_csv_path):
    with pytest.raises(InvalidAddressException):
        read_addresses_in_csv(incorrect_list_csv_path)
