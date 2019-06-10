import random
import subprocess
import psutil
import yaml

from common.global_variable import DEFAULT_MASTER_SERVER, DEFAULT_DB_CONNECTION

###############################################################################

# General config
RUNTIME_MASTER_SERVER = "MASTER_SERVER"
RUNTIME_GPU_INFO = "GPU_INFO"
RUNTIME_FAKE_GPU = "FAKE_GPU"
RUNTIME_RUN_ONCE = "RUN_ONCE"
RUNTIME_WORKER_MACHINE_TYPE = "WORKER_TYPE"
RUNTIME_CONTAINER_CONFIG = "CONTAINER_CONFIG"
RUNTIME_DB_CONNECTION = "DB_CONNECTION"
RUNTIME_SYSTEM_INFO = "SYSTEM_INFO"

WORKER_MACHINE_DEEPCLUSTER_STANDARD = "DEEPCLUSTER_STANDARD"
WORKER_MACHINE_PROVISIONED = "PROVISIONED"

# Stage specific config
WORKER_REGISTER = "REGISTER"
REGISTER_FORCE_REGISTRATION = "FORCE_REGISTRATION"
REGISTER_REGISTRATION_ONLY = "REGISTRATION_ONLY"
REGISTER_FAKE_WORKER_REGISTRATION = "FAKE_WORKER_REGISTRATION"

WORKER_ENROLL = "ENROLL"
ENROLL_FAKE_ENROLL = "FAKE_ENROLL"

WORKER_POLL = "POLL"
POLL_SIMULATE_JOB = "SIMULATE_JOB"
POLL_POLL_SUCCESS_POSSIBILITY = "POLL_SUCCESS_POSSIBILITY"

WORKER_POLL_WAIT = "POLL_WAIT"

WORKER_FETCH = "FETCH"
FETCH_DOWNLOAD_CODE = "DOWNLOAD_CODE"
FETCH_DOWNLOAD_DATASET = "DOWNLOAD_DATASET"

WORKER_PRE_RUN = "PRE_RUN"

WORKER_RUN = "RUN"

WORKER_SIGNAL = "SIGNAL"
SIGNAL_FAKE_SIGNAL = "FAKE_SIGNAL"

WORKER_POST_RUN = "POST_RUN"
POST_RUN_UPLOAD_OUTPUT = "UPLOAD_OUTPUT"
POST_RUN_UPLOAD_LOG = "UPLOAD_LOG"

POST_RUN_COPY_OUTPUT_LOCAL = "COPY_OUTPUT_LOCAL"

WORKER_TASK_CLEANUP = "TASK_CLEANUP"

# Default runtime configuration
DEFAULT_CONTAINER_CONFIG = {
    # Per Nvidia docker, shared memory is default to 1GB.
    "shm_size": "1G"
}

DEFAULT_RUNTIME = {
    RUNTIME_MASTER_SERVER: DEFAULT_MASTER_SERVER,
    RUNTIME_CONTAINER_CONFIG: DEFAULT_CONTAINER_CONFIG,
    RUNTIME_DB_CONNECTION: DEFAULT_DB_CONNECTION
}

GPU_INFO_QUERIES = ["gpu_uuid",
                    "index",
                    "gpu_name",
                    "driver_version",
                    "pcie.link.gen.current",
                    "pcie.link.gen.max",
                    "pcie.link.width.current",
                    "pcie.link.width.max",
                    "memory.total"]


###############################################################################

def get_nvidia_gpu_details():
    """
    Get nvidia gpu details in dict format
    Returns:
        {
            <gpu_id>: {
                index: ..,
                gpu_name: ...
            }
        }
    """
    query_len = len(GPU_INFO_QUERIES)
    gpu_stat_query = ""
    gpu_stats = {}
    for query in GPU_INFO_QUERIES:
        if gpu_stat_query == "":
            gpu_stat_query = query
        else:
            gpu_stat_query += ("," + query)

    command = ["nvidia-smi", "--query-gpu={}".format(gpu_stat_query), "--format=csv,noheader"]
    try:
        exec_process = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        stdout, stderr = exec_process.communicate()
    except Exception as e:
        print("[Error::FATAL] Cannot get nvidia GPU info: {}".format(str(e)))
        return {}

    if stderr is not None:
        print("[Error::FATAL] Cannot get nvidia-smi output: {}".format(stderr))
        return {}

    if stdout is None:
        print("[Error::FATAL] Cannot get nvidia GPU info")
        return {}

    results = stdout.decode("utf-8").split('\n')
    for result in results:
        values = result.split(",")
        if len(values) != query_len:
            continue

        gpu_stats[values[0]] = {}
        for i in range(1, query_len):
            gpu_stats[values[0]][GPU_INFO_QUERIES[i]] = values[i].lstrip(' \t\n\r').rstrip(' \t\n\r')

    return gpu_stats


def get_system_info():
    system_info = {}
    system_info["cpu_count"] = psutil.cpu_count()
    mem = psutil.virtual_memory()
    system_info["memory_total"] = mem.total
    system_info["memory_available"] = mem.available
    disk = psutil.disk_usage('/')
    system_info["disk_total"] = disk.total
    system_info["disk_available"] = disk.free
    return system_info


class WorkerRuntime:
    keep_alive_count = -1
    worker_registrations = []

    def __init__(self, runtime_file=None):
        self.sharing = 1
        self.runtime = DEFAULT_RUNTIME

        # Load the current GPU related information.
        self.runtime[RUNTIME_GPU_INFO] = get_nvidia_gpu_details()

        # Load the system information.
        self.runtime[RUNTIME_SYSTEM_INFO] = get_system_info()

        # Override the runtime with runtime file.
        if runtime_file is not None:
            try:
                with open(runtime_file, "r") as f:
                    runtime_override = yaml.load(f)
                    for override in runtime_override.keys():
                        self.runtime[override] = runtime_override[override]

            except Exception as e:
                print("[Error::FATAL] Cannot parse runtime file: {}".format(str(e)))
                raise

        print("[INFO] Runtime configuration:")
        print(self.runtime)

    def set_gpu_sharing(self, sharing):
        self.sharing = sharing

    def get_gpu_sharing(self):
        return self.sharing

    def fake_gpu(self):
        return self.runtime.get(RUNTIME_FAKE_GPU, False)

    def master_server(self):
        return self.runtime[RUNTIME_MASTER_SERVER]

    def get_db_connection(self):
        return self.runtime[RUNTIME_DB_CONNECTION]

    def run_once(self):
        return self.runtime.get(RUNTIME_RUN_ONCE, False)

    def get_worker_machine_type(self):
        return self.runtime.get(
                    RUNTIME_WORKER_MACHINE_TYPE,
                    WORKER_MACHINE_DEEPCLUSTER_STANDARD)

    def container_configuration(self):
        return self.runtime[RUNTIME_CONTAINER_CONFIG]

    def get_fake_registration(self):
        return self.get_stage_configuration(
            WORKER_REGISTER,
            REGISTER_FAKE_WORKER_REGISTRATION)

    def force_registration(self):
        return self.get_stage_configuration(
            WORKER_REGISTER,
            REGISTER_FORCE_REGISTRATION)

    def registration_only(self):
        return self.get_stage_configuration(
            WORKER_REGISTER,
            REGISTER_REGISTRATION_ONLY)

    def get_stage_configuration(self, stage, configuration):
        if stage not in self.runtime:
            return None

        return self.runtime[stage].get(configuration, None)

    def simulate_enroll(self):
        return self.get_stage_configuration(
            WORKER_ENROLL,
            ENROLL_FAKE_ENROLL)

    def simulate_signal_keep_alive_response(self):
        if WORKER_SIGNAL not in self.runtime:
            return None

        if SIGNAL_FAKE_SIGNAL not in self.runtime[WORKER_SIGNAL]:
            return None

        sim_signal = self.get_stage_configuration(WORKER_SIGNAL, SIGNAL_FAKE_SIGNAL)
        if "keep_alive" not in sim_signal:
            return None

        if "max_success" not in sim_signal["keep_alive"]:
            return sim_signal["keep_alive"]

        if sim_signal["keep_alive"]["max_success"] == 0:
            return sim_signal["keep_alive"]

        if self.keep_alive_count == -1:
            self.keep_alive_count = \
                sim_signal["keep_alive"]["max_success"]

        if self.keep_alive_count == 0:
            return {"result": "stop"}
        else:
            self.keep_alive_count -= 1
            return sim_signal["keep_alive"]

    def is_simulate_signal_finish(self):
        if WORKER_SIGNAL not in self.runtime:
            return False

        if SIGNAL_FAKE_SIGNAL not in self.runtime[WORKER_SIGNAL]:
            return False

        # If we do not simulate keep_alive, we do not simulate finish.
        sim_signal = self.get_stage_configuration(WORKER_SIGNAL, SIGNAL_FAKE_SIGNAL)
        if "keep_alive" not in sim_signal:
            return False

        self.keep_alive_count = -1

        return True

    def get_local_output_folder(self):
        return self.get_stage_configuration(
            WORKER_POST_RUN,
            POST_RUN_COPY_OUTPUT_LOCAL)

    def get_simulated_job(self):
        return self.get_stage_configuration(
            WORKER_POLL,
            POLL_SIMULATE_JOB)

    def is_simulate_poll_no_task(self):
        poll_success_possibility = self.get_stage_configuration(
            WORKER_POLL,
            POLL_POLL_SUCCESS_POSSIBILITY)

        if poll_success_possibility is None:
            return False

        if poll_success_possibility and poll_success_possibility < 100:
            # Get a random integer betwenn 1 to 100. If it is greater
            # than the possibility, treat the poll as no task ready.
            r = random.randint(1, 101)
            if r > poll_success_possibility:
                return True

        return False

    def get_upload_output(self):
        return self.get_stage_configuration(WORKER_POST_RUN, POST_RUN_UPLOAD_OUTPUT)

    def get_upload_log(self):
        return self.get_stage_configuration(WORKER_POST_RUN, POST_RUN_UPLOAD_LOG)

    def get_download_code(self):
        return self.get_stage_configuration(WORKER_FETCH, FETCH_DOWNLOAD_CODE)

    def get_download_dataset(self):
        return self.get_stage_configuration(WORKER_FETCH, FETCH_DOWNLOAD_DATASET)

    def save_worker_registration(self, config):
        self.worker_registrations += [config]

    def get_worker_registration(self):
        return self.worker_registrations