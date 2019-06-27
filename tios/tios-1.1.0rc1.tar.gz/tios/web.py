#!/usr/bin/env python
'''
Create the web page for a simulation.
'''
import sys
from tios import environments, communication, admin, utilities
import tios.graphics as tg
import pickle
import mdtraj as mdt
import tempfile
import os
import os.path as op
import pymongo
import datetime

basedir = '/users/charlie/public_html'
tmpdir = '/users/charlie/public_html/tmp'
monwid = 4.0
monht = 0.2


def id_to_html(id, cname):
    '''
    Create the html for a web page for tios simulation with the given id
    '''

    te = communication.TiosAgent(id)
    monitors = te.monitors
    status = te.status
    offset = datetime.datetime.now() - datetime.datetime.utcnow()
    last_update = (te.last_update + offset).strftime("%d/%m/%y %H:%M:%S")
    title = te.title
    frame_rate = te.frame_rate
    interval = te.trate
    xyz = te.xyzsel
    md_code = te.md_code

    imgfile = tempfile.NamedTemporaryFile(suffix='.png', dir=tmpdir, delete=False).name

    top = te.topology
    n_atoms = top.n_atoms
    sel = te.selection
    top = top.subset(sel)
    t = mdt.Trajectory(xyz, top)
    t.unitcell_vectors = te.box
    t.topology.create_standard_bonds()
    t.make_molecules_whole()
    sel2 = t.topology.select('not type H')
    t.topology = t.topology.subset(sel2)
    t.xyz = t.xyz[:, sel2]

    for key in monitors:
        if not isinstance(monitors[key], str):
            monitors[key] = monitors[key][-1]

    imgwid = max(monwid, monht * len(monitors))
    tg.plot_molecule(imgfile, t, size=(imgwid,imgwid))
    os.chmod(imgfile, 0644)

    result = ''
    result += '<head></head>\n'
    result +='<table><tr><td rowspan=2><img src=\"../tios3.gif\"></td><td><h2>TIOS: '
    result +='Status page for simulation {} ({})</h2></td></tr>\n'.format(id, status)
    result +='<tr><td><h3>{}</h3></td></tr></table>\n'.format(title)
    result += "<table><tr><td>Last update:</td><td>{}</td></tr>".format(last_update)
    result += "<tr><td>Number of atoms:</td><td>{}</td></tr>".format(n_atoms)
    result += "<tr><td>MD code:</td><td>{}</td></tr>".format(md_code)
    result += "<tr><td>Current frame rate (/min):</td><td>{:4.1f}</td></tr>".format(frame_rate)
    result += "<tr><td>Sampling interval (ps):</td><td>{:4.0f}</td></tr></table>".format(interval)
    result += '<table><tr><td rowspan={}>'.format(len(monitors))
    result += '<img src=\"../tmp/{}\">'.format(op.basename(imgfile))
    result += '</td>\n'
    result += '<td>Timepoint</td><td>{:10.5g}</td></tr>\n'.format(float(monitors['Timepoint']))
    del monitors['Timepoint']
    for key in monitors:
        result += '<tr><td>{}</td><td>{:10.5g}</td></tr>\n'.format(key, float(monitors[key]))
    result += '</table>\n'
    return result

def register(user, email):
    '''
    Generates the web page that informs a new user of their registration details
    '''

    tios_env = environments.load_mongo_env()
    result = ''
    result += '<head></head>\n'
    result += '<center><img src=\"../tios2.gif\"></center>'
    result += '<center><h1>TIOS: The Internet of Simulations</h1></center><p>'
    
    if user is None or email is None:
        result += '<b>Error: you must supply both a user name and an email address</b><br>\n'
        return result
    try:
        password = utilities.id_generator(size=8)
        admin.add_user(user, password)
    except pymongo.errors.DuplicateKeyError:
        result += '<b>Error - this user name has already been taken.<br>\n' 
        result += 'Please try another one</b><br>\n'
        return result
    result += '<h2>Your tios registration is complete</h2><p>\n'
    result += 'Now run \'tios-config\' on each resource you use with the '
    result += 'following settings:<p>'
    result += '<table><tr><td><b>Database URL:</b></td><td>' + tios_env['DB_URL'] + '</td></tr>'
    result += '<tr><td><b>Database Port:</b></td><td>{}</td></tr>'.format( tios_env['DB_PORT'])
    result += '<tr><td><b>Database name:</b></td><td>' + tios_env['DB_NAME'] + '</td></tr>'
    result += '<tr><td><b>Username:</b></td><td>' + user + '</td></tr>'
    result += '<tr><td><b>Password:</b></td><td>' + password + '</td></tr></table><p>'
    result += ' (you can change your password using \'tios-passwd\') <br>'
    return result
