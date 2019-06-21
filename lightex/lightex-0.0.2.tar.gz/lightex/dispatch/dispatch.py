from jinja2 import Environment, FileSystemLoader
from os import path
from pathlib import Path

from ..namedconf import render_command


def set_job_id(expt, jobid):
    expt.run.jobid = jobid
    expt.run.run_name = f'{expt.run.experiment_name}-{jobid}'



def dispatch_expts (expts, engine='k8s', dry_run=False):
    if dry_run:
        print ("The following command will be run for one of experiments")
        print (render_command(expts[0]))
        return

    job_id = 0
    #job_id = str(uuid.uuid1())

    for expt in expts:
        set_job_id (expt, job_id)
        job_id += 1        

    if engine == 'k8s':
        from k8sutils import dispatch_expts
        dispatch_expts(expts)
    else:
        raise NotImplementedError(f'Unsupported dispatch engine {engine}')




'''
# older version of creating jobs via yaml

import tempfile

def render_yaml(job_config):
    # Create the jinja2 environment.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                            trim_blocks=True)

    # Pod YAML template
    data = j2_env.get_template('pod.yaml.j2').render(
        **job_config
    )

    return data



def make_job (expt, k8s_client, k8s_batch):
    job_id = expt['jobid']

    yaml = render_yaml(expt)
    tf = tempfile.NamedTemporaryFile()
    with open(tf.name, "w") as f:
        f.write(yaml)
    k8s_api = utils.create_from_yaml(k8s_client, tf.name)
    deps = k8s_batch.read_namespaced_job(f"m1-{job_id}", "default")
    print(f"Job {deps.metadata.name} created")


'''







