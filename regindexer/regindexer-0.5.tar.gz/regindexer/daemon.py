import logging
import threading

import click
import fedmsg

from regindexer.config import Config
from regindexer.indexer import Indexer

log = logging.getLogger('regindexer.daemon')


class IndexerThread(threading.Thread):
    def __init__(self, config_file):
        super(IndexerThread, self).__init__()

        self.indexer = Indexer(config_file)
        self.condition = threading.Condition()
        self.reasons = list()

    def reindex(self, reason):
        with self.condition:
            if not reason in self.reasons:
                self.reasons.append(reason)
            self.condition.notify()

    def run(self):
        while True:
            with self.condition:
                while not self.reasons:
                    self.condition.wait()
                reasons = self.reasons
                self.reasons = []

            log.info("Rebuilding index for: {}".format(", ".join(reasons)))
            try:
                self.indexer.index()
            except:
                log.exception("Error rebuilding index")


@click.command()
@click.option('-c', '--config', metavar='CONFIG_FILE',
              help='Path to config file',
              default='/etc/regindexer/config.yaml')
def main(config):
    logging.basicConfig(level=logging.INFO)

    conf = Config(config)
    match_topic = conf.daemon.topic_prefix + '.' + conf.daemon.environment + '.bodhi.compose.complete'

    indexer_thread = IndexerThread(config)
    indexer_thread.start()

    indexer_thread.reindex('Initialization')

    log.info("Listening for messages with topic {}".format(match_topic))
    for name, endpoint, topic, raw_msg in fedmsg.tail_messages(topic=match_topic):
        msg = raw_msg['msg']
        if msg.get('ctype') in ('container', 'flatpak'):
            log.info("Got %s message for ctype=%s", topic, msg['ctype'])
            # trigger rebuilding the index
            indexer_thread.reindex('Bodhi mash, ctype="%s"' % msg['ctype'])
