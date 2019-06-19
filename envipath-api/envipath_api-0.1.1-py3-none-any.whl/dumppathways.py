# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 23:21:40 2017

@author: me
"""
from requests import Session
import re


hosturl = 'https://pps.ethz.ch'


def login():
    session = Session()
    headers = {'Accept':'text/plain'}
    data = {
        'hiddenMethod': 'login',
        'loginusername': 'pps',
        'loginpassword': 'xxxxxxxx'
    }
    response = session.post(hosturl, data=data, headers=headers, allow_redirects=True, verify=False)
    return session


# does not seem to have any effect
# probably all wrong
def logout(session):
    headers = {'Accept':'text/plain'}
    data = {
        'hiddenMethod': 'logout',
    }
    response = session.post(hosturl, data=data, headers=headers, allow_redirects=True, verify=False)
    return response



headers={"Accept":"application/json"}
def dump_links_from_pathway(session, pw):
    nodes = {}
    for node in pw['nodes']:
        try:
            nodes[node['id']] = node['smiles']
        except KeyError:
            pass
    linkids = set()
    for link in pw['links']:
        linkids.add(link['id'])
    for linkid in linkids:
        edge = session.get(linkid, headers=headers, verify=False).json()
        substrates = [ nodes[s['id']] for s in edge['startNodes']]
        products = [ nodes[p['id']] for p in edge['endNodes']]
        # in theory it would be nice to get the simple rule responsible for the reaction
        # but seemingly only composite rules are linked. 
        # TODO: check for other solutions
        match = re.search("predicted by (bt\d+)$", edge['name'])
        rule = match.group(1) if match else edge['name']
        yield substrates, rule, products

if __name__ == '__main__':
    from sys import argv
    from os.path import isfile
    session = login()
    for url in argv[1:]:
        if isfile(url):
           from json import loads
           pw = loads(open(url).read().strip().replace("'",'"').replace(": False",": false").replace(": True",": true"))
        else:
           pw = session.get(url, headers=headers, verify=False).json()
        for s, r, p in dump_links_from_pathway(session, pw):
            print("{0}\t{1}\t{2}".format(".".join(s),r,".".join(p)))
    logout(session) 

