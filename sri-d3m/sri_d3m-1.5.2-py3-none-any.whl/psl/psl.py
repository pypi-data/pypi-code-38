import os
import subprocess
import tempfile

from psutil import virtual_memory

from sri.common import constants
from sri.common import util
from sri.psl import hyperparams

# This used to be a primitive hyperparameter, but it ran afoul of pipeline validation code,
# because when the validator generates this path, it differs from the value in the submitted
# pipeline.  Kind of stupid, but so be it.
PSL_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'psl', 'run')

# It is on the user to make sure that the subs have no collisions or order dependency.
def run_model(model_name,
        psl_hyperparams: hyperparams.PSLHyperparams,
        data_template_subs = {}, model_template_subs = {},
        lazy = False,
        int_args = False, int_ids = False,
        data_path = None):
    if (data_path is None):
        data_path = os.path.abspath(PSL_TEMP_DIR)

    logger = util.get_logger(__name__)
    logger.debug("Running PSL model, %s, with data from '%s'", model_name, data_path)

    # TODO(eriq): We need a directory to run things in.
    run_dir = data_path

    data_template_subs[constants.DATA_DIR_SUB] = run_dir
    data_template_path = os.path.join(constants.PSL_CLI_DIR, "%s_template.data" % (model_name))
    data_file_path = os.path.join(run_dir, '%s.data' % (model_name))
    _instantiate_template(data_template_path, data_file_path, data_template_subs)

    model_template_path = os.path.join(constants.PSL_CLI_DIR, "%s_template.psl" % (model_name))
    model_path = os.path.join(run_dir, '%s.psl' % (model_name))
    _instantiate_template(model_template_path, model_path, model_template_subs)

    values = _run_psl(model_path, data_file_path, run_dir, psl_hyperparams, lazy, int_args, int_ids)

    return values

def _instantiate_template(template_path, out_path, subs):
    with open(out_path, 'w') as outFile:
        with open(template_path, 'r') as inFile:
            for line in inFile:
                for (find, replace) in subs.items():
                    line = line.replace(find, replace)
                outFile.write(line)

# Returns all targets read from the file.
# Returns: {predicate: {(atom args): value, ...}, ...}
def _parse_psl_output(out_dir, int_args = False):
    values = {}

    for filename in os.listdir(out_dir):
        path = os.path.join(out_dir, filename)

        if (not os.path.isfile(path)):
            continue

        predicate = os.path.splitext(filename)[0]
        values[predicate] = {}

        with open(path, 'r') as inFile:
            for line in inFile:
                line = line.strip()

                if (line == ''):
                    continue

                parts = line.split("\t")

                if (int_args):
                    args = [int(arg.strip("'")) for arg in parts[0:-1]]
                else:
                    # TODO(eriq): What if the constant actual contains a terminal single quote.
                    args = [arg.strip("'") for arg in parts[0:-1]]

                val = float(parts[-1])

                values[predicate][tuple(args)] = val

    return values

# See if we can get a response for the named database.
def _postgres_database_available(postgresDBName):
    command = "psql '%s' -c ''" % (postgresDBName)

    try:
        subprocess.check_call(command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, shell = True)
        # print("Postgres successfully discovered.")
    except subprocess.CalledProcessError:
        # print("Postgres not found - using H2 instead.")
        return False

    return True

# Run the PSL model using the CLI and return the output (stdout).
def _run_psl(model_path, data_file_path, run_dir,
        psl_hyperparams, lazy = False,
        int_args = False, int_ids = False):
    logger = util.get_logger(__name__)


    out_dir = os.path.join(run_dir, constants.RUN_OUT_DIRNAME)

    inference = '--infer'
    if (lazy):
        inference = '--infer org.linqs.psl.application.inference.LazyMPEInference'

    memory_bytes = virtual_memory().total

    args = [
        "java -Xms%d" % (int(memory_bytes * psl_hyperparams['jvm_memory'])),
        "-jar '%s'" % (constants.PSL_CLI_JAR),
        inference,
        "--model '%s'" % (model_path),
        "--data '%s'" % (data_file_path),
        "--output '%s'" % (out_dir),
        # If we are not running lazy, take the cowards way out and ignore
        # access exceptions.
        '-D persistedatommanager.throwaccessexception=false' if not lazy else '',
        '--int-ids' if int_ids else '',
    ]
    args += _get_hyperparam_options(psl_hyperparams)
    psl_command = " ".join(args)

    logger.debug("Invoking PSL with command: %s", psl_command)

    psl_output = ''
    try:
        psl_output = str(subprocess.check_output(psl_command, shell = True), 'utf-8')
    except subprocess.CalledProcessError as ex:
        print("Failed to run PSL")
        print(psl_output)
        raise ex

    return _parse_psl_output(out_dir, int_args)

def _get_hyperparam_options(psl_hyperparams):
    options = []

    max_threads = psl_hyperparams['max_threads']
    if (max_threads > 0):
        options.append("-D parallel.numthreads=%d" % (max_threads))

    admm_iterations = psl_hyperparams['admm_iterations']
    if (admm_iterations > 0):
        options.append("-D admmreasoner.maxiterations=%d" % (admm_iterations))

    postgres_db_name = psl_hyperparams['postgres_db_name']
    if (postgres_db_name and _postgres_database_available(postgres_db_name)):
        options.append("--postgres '%s'" % (postgres_db_name))

    return options
