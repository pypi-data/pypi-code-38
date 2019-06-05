'''
   Copyright 2019 nolim1t.co

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

# File notify libraries
import inotify.adapters

# Dropbox Libraries
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# toml libraries
import toml

# System libraries
import os
import time
import logging
import signal # Signal Handling Stuff
import sys # System Stuff

from os.path import expanduser
from pathlib import Path

# Script defaults

home = expanduser("~")
config_dir = home + '/.lncm'
config_path = config_dir + '/nodebackup.toml'

if not Path(config_dir).is_dir():
    print("Directory .lncm doesn't exist")
    sys.exit() # TODO: create this and don't exit
else:
    print("Directory .lncm exists")

if not Path(config_path).exists():
    print("Config file does not exist")
    sys.exit()
else:
    print("Checking config")

try:
    configuration = toml.load(config_path, _dict=dict)
except:
    print("Failed to load config")
    sys.exit(1)

if not 'logfile' in configuration:
    print("no logfile path defined!")
    sys.exit(1)

if not 'provider' in configuration:
    print("No provider = 'providername' defined in toml root")
    sys.exit(1)

if not 'apikeys' in configuration:
    print("No section called [apikeys] in configuration file, please define this")
    sys.exit(1)

if not 'nodename' in configuration:
    print("'nodename' is not defined in toml root")
    sys.exit(1)

providername = configuration['provider']
nodename = configuration['nodename']
# Check pidfile
if not 'pidfile' in configuration:
    pidfile = "/var/run/nodebackup.pid"
else:
    pidfile = configuration['pidfile']

# Check backup file
if not 'backupfile' in configuration:
    # Default path
    backupfile = "/media/important/important/lnd/data/chain/bitcoin/mainnet/channel.backup"
else:
    # Define the location of the backup in config
    backupfile = configuration['backupfile']

# Set up logging
logging.basicConfig(filename=configuration['logfile'], level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# Handle and exit
def handler_stop_signals(signum, frame):
    logging.info("Caught Terminate signal - exiting")
    logging.debug("Signal %d received" % signum)
    if Path(pidfile).exists():
        logging.info("Cleaning up PID file")
        os.unlink(pidfile)
    sys.exit(0)


if configuration['apikeys'][providername] is None:
    print("No API key for " + providername + " is defined")
    sys.exit()



# # See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
# Define dropbox connection
logging.info('Started daemon')
logging.info('Dropbox connection initialized')
dbx = dropbox.Dropbox(configuration['apikeys'][providername])

# Add handlers
signal.signal(signal.SIGTERM, handler_stop_signals)
signal.signal(signal.SIGHUP, handler_stop_signals)
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGQUIT, handler_stop_signals)

def dropboxbackup(filename, host='default'):
    logging.info('Dropbox backup started')
    filearray = os.path.split(filename)
    pathname = '/lncm/channel_backups/' + host + '/' + filearray[len(filearray) - 1]
    with open(filename, 'rb') as f:
        logging.info("Uploading " + filename + " to dropbox " + pathname)
# Actually do the upload now
        try:
            dbx.files_upload(f.read(), pathname, mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and
                err.error.get_path().reason.is_insufficient_space()):
                logging.fatal("Not enough space on dropbox")
                sys.exit("Not enough space on dropbox")
            elif err.user_message_text:
                logging.warn("Dropbox system error: " + err.user_message_text)
            else:
                logging.warn("Generic system error: " + err)                

def watch(fileparam):
    while True:
        if Path(fileparam).exists():
            i = inotify.adapters.Inotify()
            i.add_watch(fileparam)
            logging.info("Watching file " + fileparam + " for changes")
            for event in i.event_gen(yield_nones=False):
                (_, type_names, path, filename) = event
                logging.debug("File changed with flag: " + str(type_names))
                if type_names == ['IN_MODIFY']:
                    logging.info('File ' + fileparam + ' Changed.. uploading to defined cloud services')
                    dropboxbackup(filename=fileparam, host=nodename)
        else:
            logging.warn("File doesn't exist.. waiting for 10 minutes before checking again")
            time.sleep(600)      

def startdaemon():
    # Forking stuff
    try:
        pid = os.fork()
        if pid > 0:
            logging.info("Running process as PID: %d" % pid)
            print('Running process as PID %d' % pid)
            # Check if writing is possible to the specified pid file
            if os.access(os.path.dirname(os.path.realpath(pidfile)), os.W_OK):
                print('Using %s as pidfile' % pidfile)
                logging.info('Using %s as pidfile' % pidfile)
                with open(pidfile, 'w') as pidfilepointer:
                    pidfilepointer.write("%d" % pid)
            else:
                print('Cannot write to %s' % pidfile)
                logging.warn('Cannot write to %s' % pidfile)
            os._exit(0)
    except:
        logging.fatal("Unable to fork")
        print('Unable to fork')
        os._exit(1)
    
    watch(backupfile)
    
    # End Daemon function

# Main entrypoint
def main():
    startdaemon()

if __name__ == '__main__':
    main()