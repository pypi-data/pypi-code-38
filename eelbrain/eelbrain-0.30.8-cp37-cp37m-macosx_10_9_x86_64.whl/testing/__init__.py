# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import pytest

pytest.register_assert_rewrite('eelbrain.testing._testing')

from ._testing import (
    gui_test,
    requires_mne_sample_data, requires_pyarrow, requires_r_ez,
    skip_on_windows,
    TempDir, working_directory,
    assert_dataset_equal, assert_dataobj_equal, assert_source_space_equal,
    file_path, import_attr, path,
)
