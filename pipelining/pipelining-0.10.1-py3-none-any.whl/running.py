from time import sleep
from .structure import Pipeline
from .stats import compute_pipe_sizes, compute_throughput

def default_report_callback(throughputs: dict, pipe_sizes: dict):
    print(throughputs)
    print(pipe_sizes)

def run_forever(pipeline: Pipeline, report_freq=10, report_callback=None):
    report_callback = report_callback or default_report_callback

    pipeline.start()
    
    try:
        while True:
            sleep(report_freq)
            throughputs = compute_throughput(pipeline)
            pipe_sizes = compute_pipe_sizes(pipeline)
            report_callback(throughputs, pipe_sizes)
    except KeyboardInterrupt:
        pipeline.terminate()
