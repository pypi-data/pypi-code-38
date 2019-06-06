""" Provide a highlevel phono3py workflow for computing 3rd order force constants """

from hilde.tasks import calculate_socket
from hilde.helpers.restarts import restart
from hilde.phonopy.workflow import bootstrap

from .postprocess import postprocess

def run_phono3py(postprocess_args=None, **kwargs):
    """ high level function to run phono3py workflow """

    args = bootstrap(name="phono3py", **kwargs)

    completed = calculate_socket(**args)

    if not completed:
        restart()
    else:
        print("Start postprocess.")
        if postprocess_args is None:
            postprocess_args = {}
        args.update(postprocess_args)
        postprocess(**args)
        print("done.")
