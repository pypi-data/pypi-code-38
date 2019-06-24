from totec.client import JobClient
from totec.store import InMemoryStore
from totec.backend import RedisBackend, SqsBackend
from totec.listener import JobListener


def new_backend(config):
    ty = config.get("type")
    if ty == "redis":
        return RedisBackend.from_config(config)
    if ty == "sqs":
        return SqsBackend.from_config(config)
    raise ValueError("No such backend {}".format(ty))


def new_store(config):
    ty = config.get("type")
    if ty == "in-memory":
        return InMemoryStore()
    raise ValueError("No such store {}".format(ty))


def new_job_client(config, store=None, backend=None):
    url_template = config["url_template"]
    queue_template = config["queue_template"]
    store = store or new_store(config["store"])
    backend = backend or new_backend(config["backend"])
    return JobClient(store, backend, url_template, queue_template)


def new_job_listener(config):
    queue_names = config["queue_names"]
    outputs_encoder = config["outputs_encoder"]
    backend = new_backend(config["backend"])
    return JobListener(backend, queue_names, outputs_encoder)
