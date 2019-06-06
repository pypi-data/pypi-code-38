from pathlib import Path

import pytest

import libflavour


yaml_example_files = [("libflavour/test/data/example_project.yaml", True)]


@pytest.mark.parametrize("yaml_filename, valid", yaml_example_files)
def test_validate_example_addon(yaml_filename, valid):
    with Path(yaml_filename).open() as f:
        if valid:
            libflavour.load_project(f.read())
        else:
            with pytest.raises(libflavour.exceptions.ValidationException):
                libflavour.load_project(f.read())
