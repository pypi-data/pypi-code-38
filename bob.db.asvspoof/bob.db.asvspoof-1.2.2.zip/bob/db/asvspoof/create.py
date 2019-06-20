#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Fri 27 Nov 13:43:22 2015

"""This script creates the ASVspoof database in a single pass.
"""

from __future__ import print_function

import fnmatch

import glob

from .models import *
import os.path


def add_file(session, protocol, purpose, attack_type, path, group, client_id='undefined', gender='undefined'):
    db_client = session.query(Client).filter(Client.id == client_id).first()
    if db_client == None:
        db_client = Client(client_id, gender, group)
        session.add(db_client)

    db_file = session.query(File).filter(File.path == path).first()
    if db_file == None:
        db_file = File(db_client, purpose, attack_type, path, group)
        session.add(db_file)

    # add find the correct protocol
    db_protocol = session.query(Protocol).filter(Protocol.name == protocol).first()
    if db_protocol == None:
        raise ValueError("Protocol %s should have been created before adding files to the database!" % (protocol))

    # link file and the protocol
    session.add(ProtocolFiles(db_protocol, db_file))

def add_four_columns(session, samplesdir, filename, protocol, group, splitline, gender):
    client = splitline[0]
    samplesfolder = splitline[0]
    samplename = splitline[1]
    attack_type = 'undefined'

    # CM and ASV protocols have different order of columns!!
    if protocol == 'CM' or protocol == 'AS':
        attack_indicator = splitline[2]
        human_indicator = splitline[3]
    else:
        attack_indicator = splitline[3]
        human_indicator = splitline[2]

    # if the sample is genuine - CM protocol
    if human_indicator == 'human':
        purpose = 'real'
    # if the sample is genuine - ASV protocol
    elif human_indicator == 'genuine':
        purpose = 'real'
    # if the sample is an attack
    elif human_indicator == 'spoof':
        purpose = 'attack'
        attack_type = attack_indicator
    # if the sample is an impostor
    elif human_indicator == 'impostor':
        purpose = 'impostor'
    else:
        raise ValueError("File `%s' should specify for sample `%s' whether "
                         "it is data from human, impostor, or it's spoofed." %
                         (filename, " ".join(splitline)))
    sample_path = os.path.join(samplesdir, samplesfolder, samplename)
    add_file(session, protocol, purpose, attack_type, sample_path, group, client_id=client, gender=gender)


def add_enrollments(session, samplesdir, filename, protocol, group, line, gender):
    # the delimiter is ','
    splitline = (line.strip()).split(',')
    client = splitline[0]
    samplesfolder = splitline[0]
    purpose = 'enroll'
    attack_type = 'undefined'
    for samplename in splitline[1:]:
        sample_path = os.path.join(samplesdir, samplesfolder, samplename)
        if samplename[0] == 'D':  #belongs to the dev group
            group = 'dev'
        elif samplename[0] == 'E':  #belongs to the eval group
            group = 'eval'
        else:
            raise ValueError("Uknown client's type %s in protocol file `%s'. Client's name should start either "
                             "with 'D' or with 'E'." %
                             (filename, samplename))

        add_file(session, protocol, purpose, attack_type, sample_path, group, client_id=client, gender=gender)

def add_one_column(session, protocol, group, line):
    client = 'undefined'
    samplesfolder = line[0:6]
    purpose = 'attack'
    attack_type = 'unknown'
    samplename = line
    gender = 'undefined'
    samplesdir = os.path.join('eva_release', 'wav')
    sample_path = os.path.join(samplesdir, samplesfolder, samplename)
    add_file(session, protocol, purpose, attack_type, sample_path, group, client_id=client, gender=gender)

def add_protocol_samples(session, protodir, samplesdir, filename, protocol, group, gender):
    # read and add file to the database
    with open(os.path.join(protodir, filename)) as f:
        lines = f.readlines()
    for line in lines:
        splitline = (line.strip()).split(' ')

        # this is the protocol used in the ASVspoof 2015 competition
        if protocol == 'AS':
            samplesdir = os.path.join('ASVspoof2015_development', 'wav')
            if group == 'eval':
                # samplesdir is different for eval files, so we don't use it in the call
                add_one_column(session, protocol, group, splitline[0])
                continue

        # in ASV protocol enrollment file has 6 columns and different structure
        if group == 'enroll':
            # have to add enrollment data separately
            add_enrollments(session, samplesdir, filename, protocol, group, splitline[0], gender)
        else:
            # all the other files have four column format
            add_four_columns(session, samplesdir, filename, protocol, group, splitline, gender)

def init_database(session, protodir, samplesdir, protocol_file_list):
    """Defines all available protocols"""

    for filename in protocol_file_list:
        # skip hidden files
        # if filename.startswith('.'):
        #     continue
        # skip directories
        # if os.path.isdir(os.path.join(protodir, filename)):
        #     continue

        print ("Processing file %s" % filename)
        # remove extension
        fname = os.path.splitext(os.path.basename(filename.strip()))[0]
        # parse the name
        s = fname.split('_')
        print ("Basename %s" % fname)

        group = s[1]  #train, develop, or evaluation
        protocol = s[0].upper()
        # processing countermeasure protocol
        if protocol == 'CM':
            gender = 'undefined'
        # protocol to evaluate response of an ASV system to the spoofing attacks
        elif protocol == 'ASV':
            group = s[2]  #group is at different place for ASV protocol
            gender = s[1]
            protocol += '-' + gender  #ASV protocols include gender in their names
        # protocol used in the ASVspoof 2015 competition
        elif protocol == 'AS':
            gender = 'undefined'
        else:
            raise ValueError("Protocol file `%s' is not supported." % filename)

        # map the group name
        if group == 'development':
            group = 'dev'
        if group == 'develop':
            group = 'dev'
        if group == 'evaluation':
            group = 'eval'
        if group == 'enrolment':
            group = 'enroll'

        # add protocol only if it does not exist
        db_protocol = session.query(Protocol).filter(Protocol.name == protocol).first()
        if db_protocol == None:
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

    # ASV protocol files
    protocol_file_list = glob.glob(os.path.join(args.protodir, 'ASV_*'))
    init_database(s, args.protodir, args.samplesdir, protocol_file_list)

    # CM protocol files
    protocol_file_list = glob.glob(os.path.join(args.protodir, 'cm_*'))
    init_database(s, args.protodir, args.samplesdir, protocol_file_list)

    # AS protocol files
    protocol_file_list = glob.glob(os.path.join(args.protodir, 'as_*'))
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
                        default='wav',
                        metavar='DIR',
                        help="Change the relative path to the directory containing the audio samples definitions for asvspoof database (defaults to %(default)s)")

    parser.add_argument('-P', '--protodir', action='store',
                        default='/Users/pavelkor/Documents/pav/idiap/src/bob.db.asvspoof/bob/db/asvspoof/protocols/',
                        metavar='DIR',
                        help="Change the relative path to the directory containing the protocol definitions for asvspoof attacks (defaults to %(default)s)")

    parser.set_defaults(func=create)  # action
