
from vat_utils.command import define_argument

run_build_args = [
    define_argument('build_context_config_source'),
    define_argument('build_config_path'),
    define_argument('--verbose', action='store_true'),
]

terraform_init_args = [
    define_argument('config_source'),
    define_argument('terraform_dir')
]
