import os
from pathlib import Path
import json

import pytest
from click.testing import CliRunner
from eth_keyfile import create_keyfile_json
from eth_utils import is_address

from deploy_tools.cli import main


@pytest.fixture()
def keystores(tmp_path, account_keys, key_password):
    """paths to keystore files"""
    paths = []
    for i, private_key in enumerate(account_keys[:2]):
        file_path = tmp_path / f"keyfile-{i}.json"
        file_path.write_text(
            json.dumps(
                create_keyfile_json(
                    private_key.to_bytes(), key_password.encode("utf-8")
                )
            )
        )
        paths.append(file_path)

    return paths


@pytest.fixture()
def output_file(tmp_path):
    return tmp_path / "test.json"


@pytest.fixture()
def keystore_file_path(tmp_path, keystores, key_password):
    """path to keystore of account[1]"""
    return keystores[1]


@pytest.fixture()
def key_password():
    """password used for the keystores"""
    return "test_password"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def go_to_root_dir():
    current_path = os.getcwd()
    os.chdir(Path(__file__).parent.parent)
    yield
    os.chdir(current_path)


@pytest.mark.usefixtures("go_to_root_dir")
def test_default_compile(runner):
    result = runner.invoke(main, "compile -d testcontracts")
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_minimize_compile(runner):
    result = runner.invoke(main, "compile -d testcontracts --minimize")
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_contract_names_compile(runner):
    result = runner.invoke(
        main, "compile -d testcontracts --contract-names OtherContract"
    )
    assert result.exit_code == 0

    with open("build/contracts.json") as f:
        contract_assets = json.load(f)
        assert "TestContract" not in contract_assets
        assert "OtherContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_contract_output_file(runner, output_file):
    result = runner.invoke(main, f"compile -d testcontracts -o {output_file}")
    assert result.exit_code == 0

    with output_file.open() as f:
        contract_assets = json.load(f)
        assert "TestContract" in contract_assets


@pytest.mark.usefixtures("go_to_root_dir")
def test_unknown_contract_names_compile(runner):
    result = runner.invoke(
        main, "compile -d testcontracts --contract-names TestContracto"
    )
    assert result.exit_code == 2


@pytest.mark.usefixtures("go_to_root_dir")
def test_deploy_simple_contract(runner):
    result = runner.invoke(main, "deploy OtherContract -d testcontracts --jsonrpc test")
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_contract_with_arguments(runner):
    result = runner.invoke(
        main,
        "deploy -d testcontracts --jsonrpc test -- ManyArgumentsContract "
        + "0 -1 -2 true 0x00D6Cc1BA9cf89BD2e58009741f4F7325BAdc0ED 0x00",
    )
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_transaction_parameters(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 200000 --gas-price 20 --nonce 0",
    )
    assert result.exit_code == 0
    assert is_address(result.output[:-1])


@pytest.mark.usefixtures("go_to_root_dir")
def test_transaction_parameters_wrong_gas(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 100 --gas-price 20 --nonce 0",
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("go_to_root_dir")
def test_transaction_parameters_wrong_gas_price(runner):
    result = runner.invoke(
        main,
        "deploy OtherContract -d testcontracts --jsonrpc test "
        + "--gas 200000 --gas-price -1 --nonce 0",
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("go_to_root_dir")
def test_keystore(runner, keystore_file_path, key_password):
    result = runner.invoke(
        main,
        f"deploy OtherContract -d testcontracts --jsonrpc test --keystore {keystore_file_path}",
        input=key_password,
    )
    assert result.exit_code == 0


@pytest.mark.usefixtures("go_to_root_dir")
def test_keystore_wrong_nonce(runner, keystore_file_path, key_password):
    result = runner.invoke(
        main,
        f"deploy OtherContract -d testcontracts --jsonrpc test --nonce 100 --keystore {keystore_file_path}",
        input=key_password,
    )
    assert result.exit_code == 1
