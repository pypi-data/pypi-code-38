import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import logging


logging.basicConfig()
sched = BackgroundScheduler()

# if change the time, you must change it to notifies me and etc.
# @sched.scheduled_job('interval', minutes=4)

def scheduled_job():
    print("schadule start...")
    subprocess.call('python manage.py handlingobjectsupdates', shell=True, close_fds=True)


def every_day():
    print("subscription start...")
    subprocess.call('python manage.py subscriptions_management', shell=True, close_fds=True)


def every_hours():
    print("subscription start...")
    subprocess.call('python manage.py file_encrypt', shell=True, close_fds=True)


sched.add_job(scheduled_job, 'interval', minutes=4)
sched.add_job(every_hours, 'interval', hours=1)
sched.add_job(every_day, 'cron',  hour=9, minute=10)

sched.start()

# @sched.scheduled_job('cron', day_of_week='*', hour='*', minute='*/3')
# from apscheduler.schedulers.blocking import BlockingScheduler
#
# sched = BlockingScheduler()
#
# @sched.scheduled_job('interval', seconds=10)
# def timed_job():
#     print('This job is run every 10 seconds.')
#
# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
# def scheduled_job():
#     print('This job is run every weekday at 10am.')
#
# sched.configure(options_from_ini_file)
# sched.start()