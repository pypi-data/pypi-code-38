import logging
import pathlib
import time
import threading
from juliohmtools.vcswatchclient import VCSWatchClient

logger = logging.getLogger(__name__)

class VCSWatch():
    """
    A class that keeps watch over a remote Version Control System repository
    and delagates action to a handler when new commits or tags are created.

    It uses a polling mechanism to request the remote repository for the
    lastest commit revision. If there are changes, handler functions are called
    to notify any interested parties.
    """

    client = None
    handlers = list()
    cachedir = '/var/lib/vcswatch'

    polling_interval = 300

    def set_client(self, client: VCSWatchClient):
        '''
        Client that will be used to fetch information about the remote repository.
        '''
        self.client = client

    def add_handler(self, handler):
        '''
        Handler functions that will be called when new commits or tags are
        created in the remote repository.

        Handler signature
        ==================
        ```
        def my_handler(client, old_rev, new_rev):
            pass
        ```

        Handler parameters
        ===================
        `client`:
            VCSWatchClient object used to connect to the remote repository

        `old_rev`:
            Old revision number that was previously kept in cache for the watch.

        `new_rev`:
            New revision number that was found in the remote repository.
        '''
        self.handlers.append(handler)

    def set_cachedir(self, dir):
        '''
        Cache directory where VCSWatch keeps information about the remote
        repository. This is necessary in order to keep track of changes
        that happen between polls.

        Default: `/var/lib/vcswatch`
        '''
        self.cachedir = dir

    def set_polling_interval(self, interval_seconds):
        '''
        How long to wait between polling requests to the remote repository.

        Default: `300 (5min)`
        '''
        self.polling_interval = interval_seconds

    def watch(self):
        if not self.client:
            raise Exception('There are no clients defined. Use VCSWatch.set_client() to define one.')

        self.client.init()
        logging.info('Watching remote repository '+str(self.client))
        logging.info('Polling interval: '+str(self.polling_interval))
        while True:
            try:
                clientrev = str(self.client.get_lastest_revision())
                clienthash = self.client.get_hash()

                if not clientrev:
                    logger.error('Not a valid revision '+str(self.client))

                if not clienthash:
                    logger.error('Not a valid hash '+str(self.client))

                local_cache_file = self.cachedir + '/' + clienthash + '.rev'
                if not pathlib.Path(local_cache_file).exists():
                    pathlib.Path(local_cache_file).touch()

                localrev = pathlib.Path(local_cache_file).read_text()
                logging.debug('Old revision acquired from local cache ['+local_cache_file+'] '+localrev)

                if localrev != clientrev:
                    logging.debug('Revision changed for client '+str(self.client))
                    for h in self.handlers:
                        h(self.client, localrev, clientrev)
                    pathlib.Path(local_cache_file).write_text(clientrev)
                    logging.debug('New revision written to local cache ['+local_cache_file+'] '+clientrev)
                else:
                    logging.debug('Polling complete. No change for '+str(self.client))
            except Exception as err:
                logging.error('Error watching remote repository: '+str(err))
                logging.debug(err, exc_info=True)
            finally:
                time.sleep(self.polling_interval)

    def watch_background(self):
        '''
        Start watch() in a background thread.

        Returns
        =======
        The thread object where the loop is running.
        '''
        th = threading.Thread(target=self.watch)
        th.start()
        return th
