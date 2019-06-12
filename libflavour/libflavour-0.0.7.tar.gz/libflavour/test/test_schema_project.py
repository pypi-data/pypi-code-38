from pathlib import Path

import pytest

import libflavour
from collections import OrderedDict

yaml_example_files = [("libflavour/test/data/example_project.yaml", True)]


@pytest.mark.parametrize("yaml_filename, valid", yaml_example_files)
def test_validate_example_addon(yaml_filename, valid):
    with Path(yaml_filename).open() as f:
        if valid:
            libflavour.load_project(f.read())
        else:
            with pytest.raises(libflavour.exceptions.ValidationException):
                libflavour.load_project(f.read())


yaml_example_files_addons = [
    (
        "libflavour/test/data/example_project.yaml",
        {
            "addon_example_1": OrderedDict(
                [
                    ("manager", "fam-python"),
                    (
                        "settings",
                        OrderedDict(
                            [
                                ("somevalue", "123"),
                                ("someothervalue", "123"),
                                ("database", "database1"),
                            ]
                        ),
                    ),
                ]
            ),
            "addon_example_2": OrderedDict([("manager", "fam-diviocloud-addon")]),
        },
    )
]


@pytest.mark.parametrize("yaml_filename, addons", yaml_example_files_addons)
def test_get_addons_from_project(yaml_filename, addons):
    with Path(yaml_filename).open() as f:
        read_addons = libflavour.get_addons(f.read())
        assert read_addons == addons
