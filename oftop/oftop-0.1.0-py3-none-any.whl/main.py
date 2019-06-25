import psutil
from pathlib import Path
import collections
import time
import os

def open_files_by_procs(process_filter=None):
    attrs = ['pid', 'name', 'username', 'status', 'open_files', 'cmdline']
    proc_iter = psutil.process_iter(attrs=attrs)

    if process_filter:
        proc_iter = (process_filter(proc) for proc in proc_iter)

    procs = {}
    for proc in proc_iter:
      try:
        procs[proc.pid] = proc.info
      except psutil.NoSuchProcess:
        pass

    return procs


def try_file_size(f):
    try:
        return f.stat().st_size
    except Exception:
        return 0

STATUS = {
    'STATUS': 'STATUS',
    'running': 'R',
    'paused': 'I',
    'sleeping': 'S',
    'disk-sleep': 'D',
    'start_pending': 'P',
    'pause_pending': 'P',
    'continue_pending': 'P', 
    'stop_pending': 'P', 
    'stopped': 'T'
}


def human_speed(speed):
    if speed < 1024:
        return f'{speed:5.1f} B/s'
    if speed < 1024 ** 2:
        return f'{speed / 1024 ** 1:5.1f} KB/s'
    if speed < 1024 ** 3:
        return f'{speed / 1024 ** 2:5.1f} MB/s'
    if speed < 1024 ** 4:
        return f'{speed / 1024 ** 3:5.1f} GB/s'
    return f'{speed / 1024 ** 4:5.1f} TB/s'


def open_files_by_file(diff, diff_time):
    files = {}
    now = time.time()

    for pid, proc in open_files_by_procs().items():
        for f in proc['open_files']:
            data = dict(proc)
            del data['open_files']
            data['pid'] = pid

            path = Path(f.path)

            data['file_pos'] = f.position
            size = try_file_size(path)
            if size is not None:
                data['file_size'] = size
                data['file_pos_percent'] = '{:3.1f}'.format(min(100, f.position / (size or 1) * 100))

            old = diff.get(f.path)
            if old is not None:
                data['old_diff_pos'] = max(old['diff_pos'], old['old_diff_pos'])
                data['diff_pos'] = (f.position - old['file_pos'])
                data['current_speed'] = (f.position - old['file_pos']) / (now - diff_time)
                if f.position < old['file_pos']:
                    data['diff_pos'] = 999999
                    data['current_speed_human'] = 'jump '
                else:
                    data['current_speed_human'] = human_speed(data['current_speed']) + ' '
            elif diff_time:
                data['old_diff_pos'] = 0
                data['diff_pos'] = f.position
                data['current_speed'] = f.position / (now - diff_time)
                data['current_speed_human'] = '{}?'.format(human_speed(data['current_speed']))
            else:
                data['old_diff_pos'] = 0
                data['diff_pos'] = 0
                data['current_speed'] = 0
                data['current_speed_human'] = human_speed(0) + ' '

            files[f.path] = data

    return files, now


def draw_screen(files):
    N, columns = os.popen('stty size', 'r').read().split()
    N = int(N) - 5
    columns = int(columns)

    SEP = ' '
    files = files.items()
    files = sorted(files, key=lambda kv: -1 * kv[1]['old_diff_pos'])
    files = sorted(files, key=lambda kv: -1 * kv[1]['diff_pos'])

    files.insert(0, ('FILE', {
        'pid': 'PID',
        'username': 'USER',
        'status': 'STATUS',
        'file_pos': 'POSITION',
        'file_size': 'SIZE',
        'file_pos_percent': 'POS',
        'current_speed_human': 'SPEED ',
        'cmdline': 'COMMAND'.split(),
    }))

    print('\033[2J')
    print('oftop v0.1.0 (Ctrl+C to quit)')
    print('')

    for i, (path, f) in enumerate(files):
        if i > N:
            break

        cmdline = ' '.join(f['cmdline'])
        print(f"{f['pid']:>5}{SEP}{f['username'][:8]:>8}{SEP}{STATUS[f['status']]:<6}{SEP}{f['file_pos']:>10}{SEP}{f['file_size']:>10}{SEP}{f['file_pos_percent']:>5}%{SEP}{f['current_speed_human']:>11}{SEP}{cmdline[:25]:<25}{SEP}{path}")

def main():
    files, timestamp = open_files_by_file({}, None)
    draw_screen(files)
    while True:
        time.sleep(time.time() + 1 - timestamp)
        files, timestamp = open_files_by_file(files, timestamp)
        draw_screen(files)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

