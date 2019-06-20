#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Fri 3 Feb 13:43:22 2017

"""This script creates the ASVspoof2017 database in a single pass.
"""

from __future__ import print_function

import fnmatch

import glob

from .models import *
import os.path


def add_file(session, protocol, path, purpose, attack_type, group, phrase_id, environment_id,
             playback_device, recording_device, client_id='undefined', gender='undefined'):
    db_client = session.query(Client).filter(Client.id == client_id).first()
    if db_client == None:
        db_client = Client(client_id, gender, group)
        session.add(db_client)

    db_file = session.query(File).filter(File.path == path).first()
    if db_file == None:
        db_file = File(db_client, purpose, attack_type, phrase_id, environment_id, playback_device, recording_device, path, group)
        session.add(db_file)

    # add find the correct protocol
    db_protocol = session.query(Protocol).filter(Protocol.name == protocol).first()
    if db_protocol == None:
        raise ValueError("Protocol %s should have been created before adding files to the database!" % (protocol))

    # link file and the protocol
    session.add(ProtocolFiles(db_protocol, db_file))

def add_2_columns(session, samplesdir, filename, protocol, group, splitline, gender):
    if protocol == 'competition':
        # in this case, there are only two columns: name of the file and phrase that was read
        samplename = splitline[0]
        samplename = samplename[:-4]  # remove extension
        phrase_id = splitline[1]

        purpose = 'spoof'  # assume always attacks
        attack_type = 'spoof'
        client = 'E0001'  # since info is hidden in this set, assume the same client
        samplesfolder = group
        environment_id = 'undefined'
        playback_device = 'undefined'
        recording_device = 'undefined'
    else:
        raise ValueError("Protocol file `%s' is not supported." % filename)

    sample_path = os.path.join(samplesdir, samplesfolder, samplename)
    add_file(session, protocol, sample_path, purpose, attack_type, group, phrase_id, environment_id,
             playback_device, recording_device, client_id=client, gender=gender)

def add_7_columns(session, samplesdir, filename, protocol, group, splitline, gender):

    if protocol == 'competition':
        samplename = splitline[0]
        samplename = samplename[:-4]  # remove extension
        purpose = splitline[1]  # attack or not
        attack_type = 'undefined'
        if purpose == 'spoof':
            attack_type = purpose
        client = splitline[2]
        samplesfolder = group

        phrase_id = splitline[3]
        environment_id = splitline[4]
        if environment_id == '-':
            environment_id = 'undefined'
        playback_device = splitline[5]
        if playback_device == '-':
            playback_device = 'undefined'
        recording_device = splitline[6]
        if recording_device == '-':
            recording_device = 'undefined'
    else:
        raise ValueError("Protocol file `%s' is not supported." % filename)

    sample_path = os.path.join(samplesdir, samplesfolder, samplename)
    add_file(session, protocol, sample_path, purpose, attack_type, group, phrase_id, environment_id,
             playback_device, recording_device, client_id=client, gender=gender)


def add_protocol_samples(session, protodir, samplesdir, filename, protocol, group, gender):
    # read and add file to the database
    with open(os.path.join(protodir, filename)) as f:
        lines = f.readlines()
    for line in lines:
        splitline = (line.strip()).split(' ')

        if len(splitline) == 2:  # eval set of the competition
            add_2_columns(session, samplesdir, filename, protocol, group, splitline, gender)
        elif len(splitline) == 7:  # train and dev sets of the competition
            add_7_columns(session, samplesdir, filename, protocol, group, splitline, gender)
        else:
            raise ValueError("Protocol file should contain either 7 items per line or 2." % filename)

def init_database(session, protodir, samplesdir, protocol_file_list):
    """Defines all available protocols"""

    for filename in protocol_file_list:
        # skip hidden files
        # if filename.startswith('.'):
        #     continue
        # skip directories
        # if os.path.isdir(os.path.join(protodir, filename)):
        #     continue

        print("Processing file %s" % filename)
        # remove extension
        fname = os.path.splitext(os.path.basename(filename.strip()))[0]
        # parse the name
        s = fname.split('_')
        print("Basename %s" % fname)

        group = s[1]  #train, develop, or evaluation
        protocol = 'competition'
        # protocol used in the ASVspoof 2017 competition
        if protocol == 'competition':
            gender = 'undefined'
        else:
            raise ValueError("Protocol file `%s' is not supported." % filename)

        # add protocol only if it does not exist
        db_protocol = session.query(Protocol).filter(Protocol.name == protocol).first()
        if db_protocol is None:
            session.add(Protocol(protocol))
            session.flush()
        # add samples from the protocol file to the database
        add_protocol_samples(session, protodir, samplesdir, filename, protocol, group, gender)


def create_tables(args):
    """Creates all necessary tables (only to be used at the first time)"""

    from bob.db.base.utils import create_engine_try_nolock

    engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))
    Client.metadata.create_all(engine)
    File.metadata.create_all(engine)


# Driver API
# ==========

def create(args):
    """Creates or re-creates this database"""

    from bob.db.base.utils import session_try_nolock

    dbfile = args.files[0]

    if args.recreate:
        if args.verbose and os.path.exists(dbfile):
            print('unlinking %s...' % dbfile)
        if os.path.exists(dbfile): os.unlink(dbfile)

    if not os.path.exists(os.path.dirname(dbfile)):
        os.makedirs(os.path.dirname(dbfile))

    # the real work...
    create_tables(args)
    s = session_try_nolock(args.type, args.files[0], echo=(args.verbose >= 2))

    # ASVspoof2017 competition protocol files
    protocol_file_list = glob.glob(os.path.join(args.protodir, 'ASVspoof2017_*'))
    init_database(s, args.protodir, args.samplesdir, protocol_file_list)

    s.commit()
    s.close()

    return 0


def add_command(subparsers):
    """Add specific subcommands that the action "create" can use"""

    parser = subparsers.add_parser('create', help=create.__doc__)

    parser.add_argument('-R', '--recreate', action='store_true', default=False,
                        help="If set, I'll first erase the current database")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Do SQL operations in a verbose way")

    parser.add_argument('-D', '--samplesdir', action='store',
                        default='',
                        metavar='DIR',
                        help="Change the relative path to the directory containing the audio samples definitions for asvspoof2017 database (defaults to %(default)s)")

    # run create database with ABSOLUTE path to --protodir
    parser.add_argument('-P', '--protodir', action='store',
                        default='/Users/pavelkor/Documents/pav/idiap/src/bob.db.asvspoof2017/bob/db/asvspoof2017/protocols/',
                        metavar='DIR',
                        help="Change the relative path to the directory containing the protocol definitions for asvspoof2017 attacks (defaults to %(default)s)")

    parser.set_defaults(func=create)  # action
