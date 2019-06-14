import sched, time 
import os
import subprocess
import logging
import sys

logging.basicConfig(level=logging.INFO)


if not os.path.exists('tasks.py'):
    logging.error('ERROR! Please, create a file named {}/tasks.py with a luigi.Task named Main'.format(os.getcwd()))
    sys.exit(1)

ORCHESTRATOR_INTERVAL = int(os.environ.get('ORCHESTRATOR_INTERVAL', 60)) # Run every minute

s = sched.scheduler(time.time, time.sleep)

logging.info('Running task Main from {}/tasks.py every {} seconds'.format(os.getcwd(), ORCHESTRATOR_INTERVAL))

def cron():
    s.enter(ORCHESTRATOR_INTERVAL, 1, cron, [])
    logging.info('Running luigi from soneti')
    with open('/tmp/results', 'a') as f:
        f.write('NOW\n')
    command = '{} -m luigi --module tasks Main'.format(sys.executable)
    output = subprocess.check_output(command.split(), shell= False)
    logging.info('Luigi results: {}'.format(output.decode('utf-8')))
    logging.info('Luigi finished. Rescheduling in {} seconds'.format(ORCHESTRATOR_INTERVAL))


s.enter(5, 1, cron, [])
s.run()
logging.info('Soneti cron finished')
