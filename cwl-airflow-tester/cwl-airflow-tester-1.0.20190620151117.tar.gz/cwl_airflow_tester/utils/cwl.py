import cwltool.load_tool as load
from schema_salad.ref_resolver import Loader


def load_job(job_file):
    loader = Loader(load.jobloaderctx.copy())
    job_order_object, _ = loader.resolve_ref(job_file, checklinks=False)
    return job_order_object