import os

from op_askpass import operations
from op_askpass.configuration import get_configuration_directory


def main() -> None:
    item_name = os.environ["OP_ASKPASS_ITEM_NAME"]
    print(
        operations.get_password_from_op(
            executable=get_configuration_directory() / "op", item_name=item_name
        )
    )
