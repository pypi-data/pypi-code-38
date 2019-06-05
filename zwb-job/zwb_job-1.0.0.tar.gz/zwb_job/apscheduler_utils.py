from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
import time


def get_scheduler(blocking=False):
    scheduler = None
    if blocking:
        scheduler = BlockingScheduler()
    else:
        scheduler = BackgroundScheduler()
    return scheduler


if __name__ == "__main__":
    scheduler = get_scheduler()
    scheduler.start()

    def job1():
        print("job1")
    scheduler.add_job(job1, "interval", seconds=1)

    @scheduler.scheduled_job("cron", second="0/3", hour="*")
    def job2():
        print("job2")

    while True:
        time.sleep(1000)
