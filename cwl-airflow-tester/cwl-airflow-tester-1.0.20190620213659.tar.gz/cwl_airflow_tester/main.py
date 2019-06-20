#! /usr/bin/env python3
import os
import sys
import uuid
import logging
import argparse
import requests

from queue import Queue
from json import dumps, loads
from os.path import join, basename, splitext, dirname
from future.moves.urllib.parse import urljoin

from cwl_airflow_tester.utils.mute import Mute
with Mute():
    from airflow.settings import DAGS_FOLDER
    from cwl_airflow_tester.utils.helpers import normalize_args, load_yaml, gen_dag_id, get_folder
    from cwl_airflow_tester.utils.cwl import load_job
    from cwl_airflow_tester.utils.checker import get_listener_thread, get_checker_thread
    from cwl_airflow_tester.utils.airflow import conf_get_default
    from cwl_airflow_tester.utils.logger import reset_root_logger
    from cwl_airflow_tester.utils.spinner import get_spinner_thread


DAG_TEMPLATE="""#!/usr/bin/env python3
from cwl_airflow import CWLDAG, CWLJobDispatcher, CWLJobGatherer
def cwl_workflow(workflow_file):
    dag = CWLDAG(cwl_workflow=workflow_file)
    dag.create()
    dag.add(CWLJobDispatcher(dag=dag), to='top')
    dag.add(CWLJobGatherer(dag=dag), to='bottom')
    return dag
dag = cwl_workflow("{}")
"""


def get_parser():
    parser = argparse.ArgumentParser(description='Run tests for CWL Airflow Parser', add_help=True)
    parser.add_argument("-t", "--test",     help="Path to the test file",               required=True)
    parser.add_argument("-o", "--output",   help="Directory to save temporary outputs", default="/tmp")
    parser.add_argument("-p", "--port",     help="Port to listen to status updates",    type=int, default=80)
    parser.add_argument("-e", "--endpoint", help="Airflow endpoint to trigger DAG",     default=conf_get_default("cli", "endpoint_url", "http://localhost:8080"))
    parser.add_argument("-r", "--range",    help="Run specific tests, format is 1,3-6,9", required=False)
    parser.add_argument("-s", "--spin",     help="Display spinner wher running", action="store_true")
    logging_level = parser.add_mutually_exclusive_group()
    logging_level.add_argument("-d", "--debug",    help="Output debug information", action="store_true")
    logging_level.add_argument("-q", "--quiet",    help="Suppress all outputs except errors", action="store_true")
    return parser


def load_data(args):
    logging.info(f"""Load test data from: {args.test}""")
    data_raw = load_yaml(args.test)

    try:
        n = []
        for r in args.range.split(","):
            s = r.split("-")
            n.extend(list(range(int(s[0]) - 1, int(s[1])))) if len(s) == 2 else n.append(int(r) - 1)
    except Exception:
        n = list(range(0, len(data_raw)))

    data_raw_filtered = [data_raw[i] for i in n if 0 <= i < len(data_raw)]

    data_formatted = {}
    for item in loads(dumps(data_raw_filtered)):
        run_id = str(uuid.uuid4())
        item.update({
            "job":  os.path.normpath(os.path.join(dirname(args.test), item["job"])),
            "tool": os.path.normpath(os.path.join(dirname(args.test), item["tool"])),
            "output_folder": get_folder(os.path.join(args.output, run_id))
        })
        data_formatted[run_id] = item
    logging.debug(f""" - {len(data_formatted)} test[s] have been loaded""")
    return data_formatted


def export_dags(data):
    dag_folder = get_folder(DAGS_FOLDER)  # creates DAGS_FOLDER if doesn't exist
    logging.info(f"""Export DAGs to: {dag_folder}""")
    dags = []
    for item in data.values():
        cwl_file = item["tool"]
        dag_file = join(dag_folder, splitext(basename(cwl_file))[0]+".py")
        if dag_file not in dags:
            with open(dag_file, 'w') as out_stream:
                out_stream.write(DAG_TEMPLATE.format(cwl_file))
                dags.append(dag_file)
                logging.debug(f""" - {dag_file}""")


def trigger_dags(data, args):
    logging.info(f"""Trigger DAGs""")
    for run_id, value in data.items():
        dag_id = gen_dag_id(value["tool"])
        job = load_job(value["job"])
        job.update({"output_folder": value["output_folder"]})
        # with Mute():
        r = requests.post(url=urljoin(args.endpoint, f"""/api/experimental/dags/{dag_id}/dag_runs"""),
                            json={
                                "run_id": run_id,
                                "conf": dumps({"job": job})
                            })
        logging.debug(f""" - {dag_id}: {run_id} \n{r.text}""")


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args, ["port", "endpoint", "debug", "quiet", "range", "spin"])

    # Set logger level
    if args.debug:
        reset_root_logger(logging.DEBUG)
    elif args.quiet:
        reset_root_logger(logging.ERROR)
    else:
        reset_root_logger(logging.INFO)

    # Load data
    data_dict = load_data(args)
    queue = Queue(maxsize=len(data_dict))

    # Export dags to dag folder
    export_dags(data_dict)

    # Start status update listener
    listener = get_listener_thread(queue=queue, port=args.port, daemon=True)
    listener.start()

    # Start checker thread
    checker = get_checker_thread(data=data_dict, daemon=False)
    checker.start()

    # Trigger all dags
    trigger_dags(data_dict, args)

    # Display spinner if  --spin
    if args.spin:
        spinner = get_spinner_thread()
        spinner.start()

    # Wait until all triggered dags return results
    checker.join()

    if any(item.get("error", None) for item in data_dict.values()):
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


