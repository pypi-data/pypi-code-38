# coding=utf-8
import os
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import time
from retry import retry
from ibm_ai_openscale_cli.enums import ResetType
from ibm_ai_openscale_cli.openscale.openscale import OpenScale

logger = FastpathLogger(__name__)
parent_dir = os.path.dirname(__file__)

class OpenScaleReset(OpenScale):

    def __init__(self, args, credentials, database_credentials):
        super().__init__(args, credentials, database_credentials)

    def reset(self, reset_type):
        if reset_type is ResetType.METRICS:
            self.reset_metrics()
        elif reset_type is ResetType.MONITORS:
            self.reset_metrics()
            self.reset_monitors()
        # "factory reset" the system
        elif reset_type is ResetType.DATAMART:
            self.delete_datamart()
            self.clean_database()

    @retry(tries=5, delay=4, backoff=2)
    def reset_metrics(self):
        '''
        Clean up the payload logging table, monitoring history tables etc, so that it restores the system
        to a fresh state with datamart configured, model deployments added, all monitors configured,
        but no actual metrics in the system yet. The system is ready to go.
        '''
        if self._database is None:
            logger.log_info('Internal database metrics cannot be reset - skipping')
        else:
            logger.log_info('Deleting datamart metrics ...')
            self._database.reset_metrics_tables(self._datamart_name)
            logger.log_info('Datamart metrics deleted successfully')

    @retry(tries=5, delay=4, backoff=2)
    def reset_monitors(self):
        '''
        Remove all configured monitors and corresponding metrics and history, but leave the actual model deployments
        (if any) in the datamart. User can proceed to configure the monitors via user interface, API, or fastpath.
        '''
        logger.log_info('Deleting datamart monitors ...')
        subscription_uids = self._client.data_mart.subscriptions.get_uids()
        for subscription_uid in subscription_uids:
            try:
                start = time.time()
                subscription = self._client.data_mart.subscriptions.get(subscription_uid)
                elapsed = time.time() - start
                logger.log_debug('TIMER: data_mart.subscriptions.get in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.explainability.disable()
                elapsed = time.time() - start
                logger.log_debug('TIMER: subscription.explainability.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.fairness_monitoring.disable()
                elapsed = time.time() - start
                logger.log_debug('TIMER: subscription.fairness_monitoring.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.performance_monitoring.disable()
                elapsed = time.time() - start
                logger.log_debug('TIMER: subscription.performance_monitoring.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.payload_logging.disable()
                elapsed = time.time() - start
                logger.log_debug('TIMER: subscription.payload_logging.disable in {:.3f} seconds'.format(elapsed))
                start = time.time()
                subscription.quality_monitoring.disable()
                elapsed = time.time() - start
                logger.log_debug('TIMER: subscription.quality_monitoring.disable in {:.3f} seconds'.format(elapsed))
                logger.log_info('Datamart monitors deleted successfully')
            except Exception as e:
                logger.log_warning('Problem during monitor reset: {}'.format(str(e)))
        logger.log_info('Datamart monitors deleted successfully')

        # finally, drop the monitor-related tables
        if self._database is None:
            logger.log_info('Internal database monitor-related tables cannot be deleted - skipping')
        else:
            logger.log_info('Deleting datamart monitor-related tables ...')
            self._database.drop_metrics_tables(self._datamart_name)
            logger.log_info('Datamart monitor-related tables deleted successfully')

    @retry(tries=5, delay=4, backoff=2)
    def delete_datamart(self):
        logger.log_info('Deleting datamart (if already present) ...')
        try:
            start = time.time()
            self._client.data_mart.delete()
            elapsed = time.time() - start
            logger.log_debug('TIMER: data_mart.delete in {:.3f} seconds'.format(elapsed))
            logger.log_info('Datamart deleted successfully')
        except Exception as e:
            ignore_exceptions = ['AIQCS0005W', 'AIQC50005W', 'AISCS0005W'] # datamart does not exist, so cannot delete
            if any(word in str(e) for word in ignore_exceptions):
                logger.log_exception(str(e))
                logger.log_info('Datamart not present, nothing to delete')
            else:
                raise e

    @retry(tries=5, delay=4, backoff=2)
    def clean_database(self):
        if self._database is None:
            logger.log_info('Internal database instance cannot be deleted - skipping')
        else:
            logger.log_info('Cleaning database ...')
            self._database.drop_existing_schema(self._datamart_name, self._keep_schema)
            logger.log_info('Database cleaned successfully')
