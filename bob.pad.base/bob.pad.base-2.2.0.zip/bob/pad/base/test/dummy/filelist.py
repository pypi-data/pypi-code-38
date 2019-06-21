
from bob.pad.base.database import FileListPadDatabase
import pkg_resources

database = FileListPadDatabase(
    name='test_filelist',
    protocol=None,
    filelists_directory=pkg_resources.resource_filename('bob.pad.base.test', 'data/example_filelist'),
    original_directory=pkg_resources.resource_filename('bob.pad.base.test', 'data'),
    original_extension=".wav",
    train_subdir='.',
    dev_subdir='.',
    eval_subdir='.',
    real_filename='for_real.lst',
    attack_filename='for_attack.lst',
    keep_read_lists_in_memory=True,
    check_original_files_for_existence=True,
    training_depends_on_protocol=False,
    models_depend_on_protocol=False
)
