from egcg_core import constants as cst


def test_constants_uniqueness():
    constants = [item for item in dir(cst) if not item.startswith("__")]
    uniq_constants = set()
    for constant in constants:
        assert constant not in uniq_constants
        uniq_constants.add(constant)
