import subprocess
from pathlib import PurePath


def get_transporter():
    xcode_root_b = subprocess.check_output(['xcode-select', '-p'])
    xcode_root = PurePath(str(xcode_root_b, 'utf-8').rstrip()).parent
    transporter_ancestor_path = xcode_root.joinpath('Applications/Application Loader.app/Contents')
    transporter_b = subprocess.check_output(['find', transporter_ancestor_path.as_posix(), '-name', 'iTMSTransporter'])
    return str(transporter_b, 'utf-8').rstrip()

transporter_path = get_transporter()

