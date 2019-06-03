import os


def check_errors_from_logs(path, log_suffix):
    """
    Check all files with name finishing on the `log_suffix` variable.
    If file doesn't ends with the line:  'Final process status is success'
    the file is reported with error
    :param path: Path to log files
    :param log_suffix: Siffix of logs files to process
    """
    logs = [f for ds, dr, files in os.walk(path) for f in files if f.endswith(log_suffix)]
    if len(logs) == 0:
        print('No logs in folder: ' + path + 'with suffix: ' + log_suffix)
    else:
        failed = 0
        for log in logs:
            log_file = os.path.join(path, log)
            with open(log_file, 'r') as fin:
                for line in fin:
                    pass
                if 'Final process status is success' != line.strip():
                    print('Error in file: ' + log_file)
                    failed += 1
        if failed == 0:
            print('Run completed')
        else:
            print('There are errors in: ' + str(failed) + '/' + str(len(logs)))
