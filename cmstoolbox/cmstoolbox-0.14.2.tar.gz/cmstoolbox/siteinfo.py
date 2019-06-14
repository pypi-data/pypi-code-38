"""
A module that returns various information about sites

:author: Daniel Abercrombie <dabercro@mit.edu>
"""


from .webtools import get_json


HOST_MAP = {
    'T1_DE_KIT':           'gridka.de',
    'T1_ES_PIC':           'pic.es',
    'T1_FR_CCIN2P3':       'ccsrm.in2p3.fr',
    'T1_IT_CNAF':          'cnaf.infn.it',
    'T1_UK_RAL':           'rl.ac.uk',
    'T1_US_FNAL':          'fnal.gov',
    'T2_AT_Vienna':        'oeaw.ac.at',
    'T2_BE_IIHE':          'iihe.ac.be',
    'T2_BE_UCL':           'ucl.ac.be',
    'T2_BR_SPRACE':        'sprace.org.br',
    'T2_BR_UERJ':          'uerj.br',
    'T2_CH_CAF':           'caf.cern.ch',
    'T2_CH_CERN':          'eoscms-srv-b2.cern.ch',
    'T2_CH_CSCS':          'cscs.ch',
    'T2_CN_Beijing':       'ihep.ac.cn',
    'T2_DE_DESY':          'desy.de',
    'T2_DE_RWTH':          'rwth-aachen.de',
    'T2_EE_Estonia':       'hep.kbfi.ee',
    'T2_ES_CIEMAT':        'ciemat.es',
    'T2_ES_IFCA':          'ifca.es',
    'T2_FI_HIP':           'csc.fi',
    'T2_FR_CCIN2P3':       'in2p3.fr',
    'T2_FR_GRIF_IRFU':     'datagrid.cea.fr',
    'T2_FR_GRIF_LLR':      'polgrid4.in2p3.fr',
    'T2_FR_IPHC':          'sbgse1.in2p3.fr',
    'T2_GR_Ioannina':      'physics.uoi.gr',
    'T2_HU_Budapest':      'kfki.hu',
    'T2_IN_TIFR':          'indiacms.res.in',
    'T2_IT_Bari':          'ba.infn.it',
    'T2_IT_Legnaro':       'lnl.infn.it',
    'T2_IT_Pisa':          'pi.infn.it',
    'T2_IT_Rome':          'roma1.infn.it',
    'T2_KR_KNU':           'knu.ac.kr',
    'T2_KR_KISTI':         'sdfarm.kr',
    'T2_MY_UPM_BIRUNI':    'biruni.upm.my',
    'T2_PK_NCP':           'ncp.edu.pk',
    'T2_PL_Swierk':        'cis.gov.pl',
    'T2_PL_Warsaw':        'icm.edu.pl',
    'T2_PT_NCG_Lisbon':    'ingrid.pt',
    'T2_RU_IHEP':          'ihep.su',
    'T2_RU_INR':           'inr.troitsk.ru',
    'T2_RU_ITEP':          'itep.ru',
    'T2_RU_JINR':          'jinr.ru',
    'T2_RU_PNPI':          'pnpi.nw.ru',
    'T2_RU_SINP':          'sinp.msu.ru',
    'T2_TH_CUNSTDA':       'nectec.or.th',
    'T2_TR_METU':          'metu.edu.tr',
    'T2_TW_NCHC':          'nchc.org.tw',
    'T2_TW_Taiwan':        'sinica.edu.tw',
    'T2_UA_KIPT':          'kharkov.ua',
    'T2_UK_London_Brunel': 'brunel.ac.uk',
    'T2_UK_London_IC':     'ic.ac.uk',
    'T2_UK_SGrid_Bristol': 'bris.ac.uk',
    'T2_UK_SGrid_RALPP':   'pp.rl.ac.uk',
    'T2_US_Caltech':       'ultralight.org',
    'T2_US_Florida':       'ufl.edu',
    'T2_US_MIT':           'mit.edu',
    'T2_US_Nebraska':      'unl.edu',
    'T2_US_Purdue':        'purdue.edu',
    'T2_US_UCSD':          'ucsd.edu',
    'T2_US_Vanderbilt':    'vanderbilt.edu',
    'T2_US_Wisconsin':     'wisc.edu',
    }


def pfn_from_phedex(site_name, lfn):
    """
    Get the PFN of a directory from phedex for a given LFN.

    :param str site_name: is the name of the site to check
    :param str lfn: is the LFN to find
    :returns: PFN of the folder
    :rtype: str
    """

    result = get_json(host='cmsweb.cern.ch',
                      request='/phedex/datasvc/json/prod/lfn2pfn',
                      params={'node': site_name,
                              'protocol': 'direct',
                              'lfn': lfn
                             },
                      use_https=True
                     )

    location = result['phedex']['mapping'][0]['pfn']
    return location

def get_domain(site):
    """ Get the domain name of a given site for use in hostname matching.

    .. Note::

       Is currently a simple map, and we'd love for someone to come along
       and improve it.

    """

    domain = HOST_MAP.get('site')

    if domain:
        return domain

    # If the key includes the site name, return the domain.
    # This is for things like T1_US_FNAL_Disk, etc.
    for key, domain in HOST_MAP.items():
        if key in site:
            return domain

    return ''


def get_site(host):
    """ Get the site of a given hostname

    .. Note::

       Is currently a simple map, and we'd love for someone to come along
       and improve it.

    """

    for site, domain in HOST_MAP.items():
        if domain in host:
            return site

    return ''
