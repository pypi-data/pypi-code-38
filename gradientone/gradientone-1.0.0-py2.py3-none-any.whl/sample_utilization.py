import time
import utilization


def run_sample_and_record_utilization(sleep_seconds=60):
    print("Starting sample test. Recording utilization start.")
    utilization.record_start()
    print("Starting test. This will take some time...")
    time.sleep(sleep_seconds)
    print("Ending test. Recording utilization end.")
    utilization.record_end()


if __name__ == "__main__":
    run_sample_and_record_utilization()
