#
# Project Librarian: Alex Urban
#              Graduate Student
#              UW-Milwaukee Department of Physics
#              Center for Gravitation & Cosmology
#              <alexander.urban@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Module containing time- and sky- coincidence search functions.
"""
__author__ = "Alex Urban <alexander.urban@ligo.org>"


# Imports.
import json
import os
import re
import sys

import healpy as hp
import numpy as np

from .gracedb_events import GW, SE, ExtTrig
from ligo.gracedb.rest import GraceDb, DEFAULT_SERVICE_URL


#######################################
# Functions for background estimation #
#######################################

def Cacc(rho_sky):
    """ Estimator for the cumulative fraction of accidental associations with
        sky coincidence better than psky. """
    if rho_sky < 1e-50: return 1.
    else:
        x = np.log10(rho_sky)
        p = [6.43375601e+00, -3.83233594e+04, 1.35768892e+01]
        return p[0] * x**3 / (p[1] + p[2]*x**3)



#########################################################
# Functions implementing the actual coincidence search. #
#########################################################

def query(event_type, gpstime, tl, th, gracedb=None, group=None, pipelines=None):
    """ Query for coincident events of type event_type occurring within a window
        of [tl, th] seconds around gpstime """

    # Perform a sanity check on the time window.
    if tl >= th:
        sys.stderr.write( "ERROR: The time window [tl, th] must have tl < th." )
        sys.exit(1)

    # Initiate correct instance of GraceDb.
    if gracedb is None:
        gracedb = GraceDb( DEFAULT_SERVICE_URL )

    # Perform the GraceDB query.
    start, end = gpstime + tl, gpstime + th
    
    if event_type!='Superevent':
        arg = '{0} {1} .. {2}'.format(event_type, start, end)
        # Return list of graceids of coincident events.
        try:
            results = list(gracedb.events(arg))
            if pipelines:
                results = [event for event in results if event['pipeline'] in pipelines]
                return results
            else:
                return results
        except:
            sys.stderr.write( "ERROR: Problem accessing GraCEDb while \
                calling gracedb.events()" )
            sys.exit(1)

    else: # We are searching for a superevent
        arg = '{0} .. {1}'.format(start, end)
        # Return list of coincident superevent_ids.
        try:
            results = list(gracedb.superevents(arg))
            if group:
                results = [superevent for superevent in results if gracedb.event( \
                           superevent['preferred_event']).json()['group']==group]
                return results
            else:
                return results
        except:
            sys.stderr.write( "ERROR: Problem accessing GraCEDb while \
                calling gracedb.events()" )
            sys.exit(1)


def search(event, tl, th, gracedb=None, group=None, pipelines=None):
    """ Perform a search for neighbors coincident in time within
        a window [tl, th] seconds around an event """

    # Identify neighbor types with their graceid strings.
    types = {'G': 'GW', 'E': 'External trigger', 'S': 'Superevent trigger',
             'T': 'Test'}
    groups = {'G': 'CBC Burst', 'E': 'External', 'S': 'Superevent'}

    # Initiate correct instance of GraceDb.
    if gracedb is None:
        gracedb = GraceDb( DEFAULT_SERVICE_URL )

    # Grab any and all neighboring events. Filter results depending on the group if specified.
    neighbors = query(groups[event.neighbor_type], event.gpstime, tl, th,
                      gracedb=gracedb, group=group, pipelines=pipelines)

    # If no neighbors, report a null result.
    if not neighbors:
        if group:
            message = "RAVEN: No %s %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], group, tl, th)
        elif pipelines:
            message = "RAVEN: No %s %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], pipelines, tl, th)
        else:
            message = "RAVEN: No %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], tl, th)
        event.submit_gracedb_log(message, tag_name=["ext_coinc"])

    # If neighbors are found, report each of them.
    else:
        for neighbor in neighbors:
            if neighbor.get('graceid'):
                gid = neighbor['graceid']
                link1 = 'events/'
                link2 = 'superevents/'
            else:
                gid = neighbor['superevent_id']
                link1 = 'superevents/'
                link2 = 'events/'
            gracedb_url = re.findall('(.*)api/', gracedb._service_url)[0]
            if group:
                message1 = "RAVEN: {0} {1} candidate found: \
                    <a href='{2}{3}".format(types[event.neighbor_type],
                                            group, gracedb_url, link1)
            else:
                message1 = "RAVEN: {0} candidate found: \
                    <a href='{1}{2}".format(types[event.neighbor_type],
                                            gracedb_url, link1)
            message1 += "%s'>%s</a> within [%+d, %+d] seconds" % (gid, gid, 
                                                                  tl, th)
            event.submit_gracedb_log(message1, tag_name=["ext_coinc"])
            try:
                gracedb.writeLabel(event.graceid, 'EM_COINC')
            except:
                pass

            if pipelines: 
                message2 = "RAVEN: {0} {1} event <a href='{2}{3}".format(
                    types[event.graceid[0]], pipelines, gracedb_url, link2)
            else:
                message2 = "RAVEN: {0} event <a href='{1}{2}".format(
                    types[event.graceid[0]], gracedb_url, link2)
            message2 += "%s'>%s</a> within window [%+d, %+d] seconds" % (
                event.graceid, event.graceid, tl, th)
            gracedb.writeLog(gid, message2, tag_name=["ext_coinc"])
            try:
                gracedb.writeLabel(gid, 'EM_COINC')
            except:
                pass

    # Return search results.
    return neighbors


def coinc_far(se_id, exttrig_id, tl, th, grb_search='GRB', se_fitsfile=None, incl_sky=False, gracedb=None):
    """ Calculate the significance of a gravitational wave candidate with the
        addition of an external astrophyical counterpart. """

    # Create the SE and ExtTrig objects based on string inputs.
    se = SE(se_id, fitsfile=se_fitsfile, gracedb=gracedb)
    exttrig = ExtTrig(exttrig_id, gracedb=gracedb)

    # Is the GW superevent candidate's FAR sensible?
    if not se.far:
        message = "RAVEN: WARNING: This GW superevent candidate's FAR is a NoneType object."
        se.submit_gracedb_log(message)
        return

    # Chooses the GCN rate based on search
    if grb_search =='GRB':
        # The combined rate of independent GRB discovery by Swift and Fermi
        # Updated based on an analysis done by Peter Shawhan
        # https://dcc.ligo.org/cgi-bin/private/DocDB/ShowDocument?docid=T1900297&version=
        gcn_rate = 547 / (365 * 24 * 60 * 60)

    elif grb_search=='subGRB':
        # Rate of subthreshold GRBs (rate of threshold plus subthreshold)
        gcn_rate = 612 / (365 * 24 * 60 * 60)
    else:
        message = "RAVEN: WARNING: Invalid search. RAVEN only considers 'GRB' and 'subGRB'."
        se.submit_gracedb_log(message)
        return

    # First, proceed with only time coincidence.
    temporal_far = (th - tl) * gcn_rate * se.far

    # Include sky coincidence if desired.
    if incl_sky:
        nside = hp.npix2nside( len(se.sky_map) )
        skymap_overlap_integral = np.dot(se.sky_map, exttrig.sky_map(nside)) / np.sum([x for x in se.sky_map]) / np.sum([y for y in exttrig.sky_map(nside)]) * len(se.sky_map)
        spatiotemporal_far = temporal_far / skymap_overlap_integral
        #psky = (4 * np.pi)**2 * np.sum( [x * y for x, y in zip(se.sky_map, exttrig.sky_map(nside))] ) / len(se.sky_map)
        #far = (th - tl) * gcn_rate * Cacc( psky ) * se.far
    else:
        spatiotemporal_far = None

    return {"temporal_coinc_far": temporal_far, "spatiotemporal_coinc_far": spatiotemporal_far}

def calc_signif_gracedb(se_id, exttrig_id, tl, th, grb_search='GRB', se_fitsfile=None, incl_sky=False, gracedb=None):
    """ Calculate and upload the coincidence false alarm rate to the 
        selected superevent in the chosen gracedb server. """

    # Create coincidence_far.json
    coincidence_far = json.dumps(coinc_far(se_id, exttrig_id, tl, th, grb_search=grb_search, se_fitsfile=se_fitsfile, incl_sky=incl_sky, gracedb=gracedb))
    
    # Create the SE and ExtTrig objects based on string inputs.
    se = SE(se_id, fitsfile=se_fitsfile, gracedb=gracedb)
    exttrig = ExtTrig(exttrig_id, gracedb=gracedb)

    gracedb_events_url = re.findall('(.*)api/', se.gracedb._service_url)[0]
    link1 = 'events/'
    link2 = 'superevents/'

    with open('coincidence_far.json', 'w+') as fp:
        fp.write(coincidence_far)
        fp.flush()
        fp.seek(0)
        message = "RAVEN: Computed coincident FAR(s) in Hz with external trigger <a href='{0}".format(gracedb_events_url + link1)
        message += "{0}'>{1}</a>".format(exttrig.graceid, exttrig.graceid)
        se.submit_gracedb_log(message, filename='coincidence_far.json', filecontents=coincidence_far, tag_name=["ext_coinc"])

        message = "RAVEN: Computed coincident FAR(s) in Hz with superevent <a href='{0}".format(gracedb_events_url + link2)
        message += "{0}'>{1}</a>".format(se.graceid, se.graceid)
        exttrig.submit_gracedb_log(message, filename='coincidence_far.json', filecontents=coincidence_far, tag_name=["ext_coinc"])
    os.remove('coincidence_far.json')

    return
