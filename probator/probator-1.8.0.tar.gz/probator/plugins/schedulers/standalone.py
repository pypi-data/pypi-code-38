import time
from datetime import datetime, timedelta

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler as APScheduler
from probator import app_config, AWS_REGIONS
from probator.constants import ConfigOption
from probator.database import db
from probator.plugins import CollectorType, BaseScheduler
from probator.plugins.types.accounts import BaseAccount, AWSAccount


class StandaloneScheduler(BaseScheduler):
    """Main workers refreshing data from AWS"""
    name = 'Standalone Scheduler'
    ns = 'scheduler_standalone'
    pool = None
    scheduler = None
    options = (
        ConfigOption('worker_threads', 20, 'int', 'Number of worker threads to spawn'),
        ConfigOption('worker_interval', 30, 'int', 'Delay between each worker thread being spawned, in seconds'),
    )

    def __init__(self):
        super().__init__()
        self.collectors = {}
        self.auditors = []
        self.region_workers = []

        self.pool = ProcessPoolExecutor(self.dbconfig.get('worker_threads', self.ns, 20))
        self.scheduler = APScheduler(
            threadpool=self.pool,
            job_defaults={
                'coalesce': True,
                'misfire_grace_time': 300
            }
        )

        self.load_plugins()

    def execute_scheduler(self):
        self.scheduler.add_job(
            self.cleanup,
            trigger='cron',
            name='cleanup',
            hour=3,
            minute=0,
            second=0
        )

        self.scheduler.add_job(
            self.schedule_jobs,
            trigger='interval',
            name='schedule_jobs',
            seconds=60,
            start_date=datetime.now() + timedelta(seconds=1)
        )

        self.scheduler.add_job(
            self.dbconfig.reload_data,
            trigger='interval',
            name='reload_dbconfig',
            minutes=5,
            start_date=datetime.now() + timedelta(seconds=3)
        )

        self.scheduler.start()

    def execute_worker(self):
        """This method is not used for the standalone scheduler."""
        print('The standalone scheduler does not have a separate worker model. Executing the scheduler will also execute the workers')
        while True:
            time.sleep(10)

    def schedule_jobs(self):
        current_jobs = {
            x.name: x for x in self.scheduler.get_jobs() if x.name not in (
                'cleanup',
                'schedule_jobs',
                'reload_dbconfig'
            )
        }
        new_jobs = []
        start = datetime.now() + timedelta(seconds=1)
        _, accounts = BaseAccount.search(include_disabled=False)

        # region Global collectors (non-aws)
        if CollectorType.GLOBAL in self.collectors:
            for wkr in self.collectors[CollectorType.GLOBAL]:
                job_name = f'global_{wkr.name}'
                new_jobs.append(job_name)

                if job_name in current_jobs:
                    continue

                self.log.info(f'Scheduling global {wkr.name} worker every {wkr.interval} minutes to start at {start}')

                self.scheduler.add_job(
                    self.execute_global_worker,
                    trigger='interval',
                    name=job_name,
                    minutes=wkr.interval,
                    start_date=start,
                    kwargs={
                        'worker': wkr
                    }
                )

                start += timedelta(seconds=30)
        # endregion

        # region AWS collectors
        aws_accounts = list(filter(lambda x: x.account_type == AWSAccount.account_type, accounts))
        for acct in aws_accounts:
            if CollectorType.AWS_ACCOUNT in self.collectors:
                for wkr in self.collectors[CollectorType.AWS_ACCOUNT]:
                    job_name = f'{acct.account_name}_{wkr.name}'
                    new_jobs.append(job_name)

                    if job_name in current_jobs:
                        continue

                    self.log.info(f'Scheduling {wkr.name} every {wkr.interval} minutes for {acct.account_name} to start at {start}')

                    self.scheduler.add_job(
                        self.execute_aws_account_worker,
                        trigger='interval',
                        name=job_name,
                        minutes=wkr.interval,
                        start_date=start,
                        kwargs={
                            'worker': wkr,
                            'account': acct.account_name
                        }
                    )

            if CollectorType.AWS_REGION in self.collectors:
                for wkr in self.collectors[CollectorType.AWS_REGION]:
                    for region in AWS_REGIONS:
                        job_name = f'{acct.account_name}_{region}_{wkr.name}'
                        new_jobs.append(job_name)

                        if job_name in current_jobs:
                            continue

                        self.log.info(
                            f'Scheduling {wkr.name} every {wkr.interval} minutes for {acct.account_name}/{region} to start at {start}'
                        )

                        self.scheduler.add_job(
                            self.execute_aws_region_worker,
                            trigger='interval',
                            name=job_name,
                            minutes=wkr.interval,
                            start_date=start,
                            kwargs={
                                'worker': wkr,
                                'account': acct.account_name,
                                'region': region
                            }
                        )
            db.session.commit()
            start += timedelta(seconds=self.dbconfig.get('worker_interval', self.ns, 30))
        # endregion

        # region Auditors
        start = datetime.now() + timedelta(seconds=1)
        for wkr in self.auditors:
            job_name = f'auditor_{wkr.name}'
            new_jobs.append(job_name)

            if job_name in current_jobs:
                continue

            if app_config.log_level == 'DEBUG':
                audit_start = start + timedelta(seconds=5)
            else:
                audit_start = start + timedelta(minutes=5)

            self.log.debug(f'Scheduling {wkr.name} every {wkr.interval} minutes to start at {audit_start}')

            self.scheduler.add_job(
                self.execute_auditor_worker,
                trigger='interval',
                name=job_name,
                minutes=wkr.interval,
                start_date=audit_start,
                kwargs={
                    'worker': wkr
                },
            )
            start += timedelta(seconds=self.dbconfig.get('worker_interval', self.ns, 30))
        # endregion

        extra_jobs = list(set(current_jobs) - set(new_jobs))
        for job in extra_jobs:
            self.log.info(f'Removing job {job} as it is no longer needed')
            current_jobs[job].remove()

    def execute_global_worker(self, *, worker):
        try:
            self.log.info(f'Starting global {worker.name} worker')
            cls = self.get_class_from_ep(worker.entry_point)
            worker = cls()
            worker.run()

        except Exception as ex:
            self.log.exception(f'Global Worker {worker.name}: {ex}')

        finally:
            db.session.rollback()
            self.log.info(f'Completed run for global {worker.name} worker')

    def execute_aws_account_worker(self, *, worker, account):
        try:
            self.log.info(f'Starting {worker.name} worker on {account}')
            cls = self.get_class_from_ep(worker.entry_point)
            worker = cls(account=account)
            worker.run()

        except Exception as ex:
            self.log.exception(f'AWS Account Worker {worker.name}/{account}: {ex}')

        finally:
            db.session.rollback()
            self.log.info(f'Completed run for {worker.name} worker on {account}')

    def execute_aws_region_worker(self, *, worker, account, region):
        try:
            self.log.info(f'Starting {worker.name} worker on {account}/{region}')
            cls = self.get_class_from_ep(worker.entry_point)
            worker = cls(account=account, region=region)
            worker.run()

        except Exception as ex:
            self.log.exception(f'AWS Region Worker {worker.name}/{account}/{region}: {ex}')

        finally:
            db.session.rollback()
            self.log.info(f'Completed run for {worker.name} worker on {account}/{region}')

    def execute_auditor_worker(self, *, worker):
        try:
            self.log.info(f'Starting {worker.name} auditor')
            cls = self.get_class_from_ep(worker.entry_point)
            worker = cls()
            worker.run()

        except Exception as ex:
            self.log.exception(f'Auditor Worker {worker.name}: {ex}')

        finally:
            db.session.rollback()
            self.log.info(f'Completed run for auditor {worker.name}')
