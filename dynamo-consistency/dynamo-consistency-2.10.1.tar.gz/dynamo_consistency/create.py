"""
Module that contains all of the threading functions needed to create a
:py:class:`dynamo_consistency.datatypes.DirectoryInfo` object.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


import os
import time
import logging
import threading
import multiprocessing
import collections

from Queue import Empty

from . import config
from . import messaging
from .datatypes import DirectoryInfo


LOG = logging.getLogger(__name__)


class ListingThread(threading.Thread):
    """
    A thread that does the listing

    :param int number: A unique number of the thread created.
                       This is used to generate a thread name and to fetch a logger.
    :param multiprocessing.Pipe recv: One end of a pipe for communicating with the master thread.
                                      Receives message here.
    :param multiprocessing.Queue send: A queue to send message to the master thread.
    :param function filler: The function that takes a path as an argument and returns:

                              - A bool saying whether the listing was successful or not
                              - A list of tuples of sub-directories and their mod times
                              - A list of tuples files inside, their size, and their mode times
    """

    out_queue = multiprocessing.Queue()
    """
    A queue where all of the listing outputs are placed.
    A master thread is expected to read from and clear this.
    """

    # Internal lock for using _in_deque
    _in_lock = threading.Lock()
    # Queue for all thread objects
    _in_deque = collections.deque()

    def __init__(self, number, recv, send, filler):
        name = 'ListingThread--%i' % number
        super(ListingThread, self).__init__(name=name)
        self.log = logging.getLogger(name)
        self.number = number
        self.recv = recv
        self.send = send
        self.filler = filler
        self.checker = messaging.Checker()


    @staticmethod
    def put_first_dir(location, directory):
        """
        Place the first set of parameters for the :py:class:`ListingThread` objects to start from.
        Should not be called once the threads are started.

        :param str location: This is the beginning of the path where we will find ``first_dir``.
                             For example, to find the first directory ``mc``, we also have to
                             say where it is. For using CMS LFNs, location would be
                             ``/store`` (where ``mc`` is inside).
        :param str directory: Name of the first directory to run over inside of location
        :returns: The name that the first DirectoryInfo object should be.
                  This is just the first directory in the directory parameter.
        :rtype: str
        """

        # Put in the first element for the queue
        # They go like, (full path of the next listing to do,
        #                name of sub-node to place the listing (blank for first level),
        #                list of previous directories, list of previous files (for retries),
        #                list of queue numbers that have failed so far)
        split_list = directory.split('/')
        dirinfo_name = split_list[0]
        first_relative = '/'.join(split_list[1:])
        LOG.debug('Taking %s, %s -> Starting from: %s, relative path: %s',
                  location, directory, dirinfo_name, first_relative)

        ListingThread._in_deque.append((os.path.join(location, dirinfo_name),
                                        first_relative,
                                        [], [], []))

        return dirinfo_name


    def run(self):
        """Runs the listing thread"""

        self.log.debug('Running queue: %i', self.number)
        running = True

        in_lock = ListingThread._in_lock
        in_deque = ListingThread._in_deque

        while running and self.checker.isrunning():
            try:
                in_lock.acquire()
                location, name, prev_dirs, prev_files, failed_list = in_deque.pop()
                if self.number in failed_list:
                    self.log.warning('Got previously failed call, putting back and sleeping')
                    in_deque.append((location, name, prev_dirs, prev_files, failed_list))

                in_lock.release()
                time.sleep(10 * (self.number in failed_list))
                self.log.debug('Getting directory with (%s, %s, %s)',
                               location, name, failed_list)

                # Call filler
                full_path = os.path.join(location, name)
                self.log.debug('Full path is %s', full_path)

                try:
                    okay, directories, files = self.filler(full_path)
                except Exception: # pylint: disable=bare-except
                    okay, directories, files = False, [], []

                self.log.debug('Got from filler: Good? %s, %i directories, %i files',
                               okay, len(directories), len(files))

                # If not okay, add _unlisted_ flag
                if not okay:

                    directories = list(set(directories + prev_dirs))
                    files = list(set(files + prev_files))

                    self.log.debug('Full dirs, and files: %s, %s', directories, files)

                    self.log.error('Giving up directory %s', full_path)
                    # _unlisted_ is used as a flag to tell our comparer something went wrong
                    files.append(('_unlisted_', 0, 0))

                # Send results to master queue
                ListingThread.out_queue.put((name, directories, files, len(failed_list)))

                # Add each directory into some input queue
                for directory, _ in directories:
                    joined_name = os.path.join(name, directory)
                    in_lock.acquire()
                    in_deque.append((location, joined_name, [], [], []))
                    in_lock.release()

                # Tell master that a job finished,
                # so it can build the final object
                self.send.put(('O', time.time()))

                self.log.debug('Finished one job with (%s, %s)', location, name)

            except IndexError:
                in_lock.release()

                # Report empty
                self.log.debug('Worker finished input queue')
                self.send.put(('A', 0))

                # Check for main process
                message = self.recv.recv()
                self.log.debug('Message from master: %s', message)
                # If permission, close
                if message == 'Close':
                    running = False
                else:
                    self.log.debug('Worker going back to check queue')

        self.recv.close()


# This function is a mess and can likely be simplified
def create_dirinfo( # pylint: disable=too-complex, too-many-locals, too-many-branches, too-many-statements
        location, first_dir, filler, object_params=None, callback=None):
    """ Create the directory information

    :param str location: This is the beginning of the path where we will find ``first_dir``.
                         For example, to find the first directory ``mc``, we also have to
                         say where it is. For using CMS LFNs, location would be
                         ``/store`` (where ``mc`` is inside).
                         This is a path.
    :param str first_dir: The name of the first directory that is inside the path of ``location``.
                          This should not be a path,
                          but the name of the directory to list recursively.
    :param filler: This is either a function that lists the directory contents given just a path
                   of ``os.path.join(location, first_dir)``, or it is a constructor that
                   does the same thing with a member function called ``list``.
                   If ``filler`` is an object constructor, the parameters for the object
                   creation must be passed through the parameter ``object_params``.
                   Both listings must return the following tuple:

                     - A bool saying whether the listing was successful or not
                     - A list of tuples of sub-directories and their mod times
                     - A list of tuples files inside, their size, and their mode times

    :type filler: function or constructor
    :param list object_params: This only needs to be set when filler is an object constructor.
                               Each element in the list is a tuple of arguments to pass
                               to the constructor.
    :param function callback: A function that is called every time master thread has finished
                              checking the child threads.
                              This can happen very many times at large sites.
                              The function is called with the main DirectoryTree as its argument
    :returns: A :py:class:`DirectoryInfo` object containing everything the directory listings from
              ``os.path.join(location, first_dir)`` with name ``first_dir``.
    :rtype: DirectoryInfo
    :raises messaging.Killed: When a site has been stopped
    """

    LOG.debug('Called create_dirinfo(%s, %s, %s, %s)',
              location, first_dir, filler, object_params)

    # Determine the number of threads
    if object_params is not None:
        n_threads = len(object_params)
    else:
        n_threads = config.config_dict()['NumThreads'] or multiprocessing.cpu_count()

    LOG.info('Listing directory %s with %i threads',
             os.path.join(location, first_dir), n_threads)

    master_conns = []
    slave_conns = []
    send_to_master = []

    dirinfo_name = ListingThread.put_first_dir(location, first_dir)

    # Spawn threads to run on this run_queue function
    threads = []

    for i_thread in xrange(n_threads):
        con1, con2 = multiprocessing.Pipe()
        queue = multiprocessing.Queue()
        master_conns.append(con1)
        slave_conns.append(con2)
        send_to_master.append(queue)

        thread = ListingThread(number=i_thread, recv=con2, send=queue,
                               filler=filler(*(object_params[i_thread])).list if \
                                   object_params is not None else filler)

        thread.start()
        threads.append(thread)

    # Build the DirectoryInfo
    building = True
    # If started in a nested directory, just build the first one
    dir_info = DirectoryInfo(dirinfo_name)

    checker = messaging.Checker()

    while building and checker.isrunning():
        try:
            # Get the info from the queue
            name, directories, files, _ = ListingThread.out_queue.get(True, 0.25)

            # Create the nodes and files
            built = dir_info.get_node(name)
            built.add_files(files)

            # Set correct node mtime for directories
            for directory, mtime in directories:
                built.get_node(directory).mtime = mtime

        except Empty:
            # When empty, check on the status of the workers
            LOG.debug('Empty queue for building.')
            LOG.info('Number of files so far built: %8i  nodes: %8i',
                     dir_info.get_num_files(), dir_info.count_nodes())

            # Process the dir_info with some callback
            if callback:
                LOG.debug('Checking callback')
                callback(dir_info)

            # Ends only if all threads are done at the beginning of this check
            threads_done = 0
            for conn in master_conns:
                LOG.debug('Waiting for thread %i', master_conns.index(conn))
                message, timestamp = send_to_master[master_conns.index(conn)].get(True)

                LOG.debug('Recieved message %s', message)
                # Count the number of threads saying their finished at the beginning
                if message == 'A':
                    threads_done += 1
                    LOG.info('Threads saying done: %i', threads_done)
                    # Send back to work, just in case not all threads are done
                    conn.send('Work')
                elif message == 'O':
                    # This thread wasn't finished at the beginning, so threads_done
                    # will not reach n_threads if the master reaches this point in the code
                    LOG.debug('Found one job, about to cycle')
                    now = time.time()
                    cycle = True
                    while cycle:
                        # Cycle through timestamps so that we do not have a backlog
                        try:
                            message, timestamp = \
                                send_to_master[master_conns.index(conn)].get(True, 1)
                            if message == 'A':
                                LOG.debug('Found end to pipe.')
                                conn.send('Work')
                                cycle = False
                            elif timestamp > now:
                                cycle = False
                        except Empty:
                            cycle = False

                else:
                    LOG.error('Weird message from pipe')

            # Check if all the threads were finished
            if threads_done == n_threads:
                LOG.debug('Done building')
                # Break out of loop of checking
                building = False

    LOG.debug('Closing all connections')

    killed = not checker.isrunning()

    # Tell connections to close
    for conn in master_conns:
        if not killed:
            conn.send('Close')
        conn.close()

    LOG.debug('Waiting for threads')
    # Wait for threads to join
    for thread in threads:
        thread.join()

    if killed:
        raise messaging.Killed('Site %s was stopped' % checker.site)

    return dir_info
