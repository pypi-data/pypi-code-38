#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import nose.tools
from .query import Database


def _query_simple_protocol_tests(protocol):
    db = Database()

    objs = db.objects(protocol)
    nose.tools.eq_(len(objs), 1800) # number of images in the protocol

    objs = db.objects(protocol, kinds='palm')
    nose.tools.eq_(len(objs), 900) # number of palm images in the protocol

    objs = db.objects(protocol, kinds='wrist')
    nose.tools.eq_(len(objs), 900) # number of wrist images in the protocol

    objs = db.objects(protocol, groups='train')
    nose.tools.eq_(len(objs), 600) # number of train images in the protocol

    objs = db.objects(protocol, groups='dev')
    nose.tools.eq_(len(objs), 600) # number of dev images in the protocol

    objs = db.objects(protocol, groups='eval')
    nose.tools.eq_(len(objs), 600) # number of dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='train')
    nose.tools.eq_(len(objs), 300) # number of palm train images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev')
    nose.tools.eq_(len(objs), 300) # number of palm dev images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval')
    nose.tools.eq_(len(objs), 300) # number of palm dev eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='train')
    nose.tools.eq_(len(objs), 300) # number of wrist train images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev')
    nose.tools.eq_(len(objs), 300) # number of wrist dev images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval')
    nose.tools.eq_(len(objs), 300) # number of wrist dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of palm dev enroll images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of palm dev probe images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of palm dev enroll eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of palm dev probe eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of wrist dev enroll images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of wrist dev probe images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of wrist eval enroll in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of wrist eval probe in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["26"])
    objs_probe = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe')
    # when quering for probes specifying exact MODEL ID, all probe files should
    # be returned:
    nose.tools.eq_(len(objs), len(objs_probe))

    if protocol.startswith('L'):
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Left/Series_2/W_o026_L_S2_Nr1.bmp')
    else:
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Right/Series_2/W_o026_R_S2_Nr1.bmp')




def _query_combined_protocol_tests(protocol):
    db = Database()

    objs = db.objects(protocol)
    nose.tools.eq_(len(objs), 7200) # number of images in the protocol

    objs = db.objects(protocol, kinds='palm')
    nose.tools.eq_(len(objs), 3600) # number of palm images in the protocol

    objs = db.objects(protocol, kinds='wrist')
    nose.tools.eq_(len(objs), 3600) # number of wrist images in the protocol

    objs = db.objects(protocol, groups='train')
    nose.tools.eq_(len(objs), 1200) # number of train images in the protocol

    objs = db.objects(protocol, groups='dev')
    nose.tools.eq_(len(objs), 1200) # number of dev images in the protocol

    objs = db.objects(protocol, groups='eval')
    nose.tools.eq_(len(objs), 1200) # number of dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='train')
    nose.tools.eq_(len(objs), 600) # number of palm train images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev')
    nose.tools.eq_(len(objs), 600) # number of palm dev images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval')
    nose.tools.eq_(len(objs), 600) # number of palm dev eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='train')
    nose.tools.eq_(len(objs), 600) # number of wrist train images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev')
    nose.tools.eq_(len(objs), 600) # number of wrist dev images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval')
    nose.tools.eq_(len(objs), 600) # number of wrist dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of palm dev enroll images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of palm dev probe images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of palm dev enroll eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of palm dev probe eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of wrist dev enroll images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of wrist dev probe images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of wrist eval enroll in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of wrist eval probe in the protocol


def test_query_L_4_protocol():
    protocol = 'L_4'
    _query_simple_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["1"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 1)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["1"])
    nose.tools.eq_(len(objs), 25*(4*2))

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["26"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["26"])
    nose.tools.eq_(len(objs), 25*(4*2))



def test_query_R_4_protocol():
    protocol = 'R_4'
    _query_simple_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["1"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 1)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["1"])
    nose.tools.eq_(len(objs), 25*(4*2))

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["26"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["26"])
    nose.tools.eq_(len(objs), 25*(4*2))


def test_query_LR_4_protocol():
    protocol = 'LR_4'
    _query_combined_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["26"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["26"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["61"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 61)
        nose.tools.eq_(obj.is_mirrored(), True)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["61"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)


def test_query_RL_4_protocol():
    protocol = 'RL_4'
    _query_combined_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["26"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["26"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["61"])
    nose.tools.eq_(len(objs), 4)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 61)
        nose.tools.eq_(obj.is_mirrored(), True)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["61"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

###############################################################################


def test_query_L_1_protocol():
    protocol = 'L_1'
    _query_simple_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["1_3"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 1)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["1_3"])
    nose.tools.eq_(len(objs), 25*(4*2))

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["26_2"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["26_3"])
    nose.tools.eq_(len(objs), 25*(4*2))



def test_query_R_1_protocol():
    protocol = 'R_1'
    _query_simple_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["1_3"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 1)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["1_3"])
    nose.tools.eq_(len(objs), 25*(4*2))

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["26_2"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["26_3"])
    nose.tools.eq_(len(objs), 25*(4*2))


def test_query_LR_1_protocol():
    protocol = 'LR_1'
    _query_combined_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["26_4"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["26_1"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["61_1"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 61)
        nose.tools.eq_(obj.is_mirrored(), True)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["61_2"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)


def test_query_RL_1_protocol():
    protocol = 'RL_1'
    _query_combined_protocol_tests(protocol)
    db = Database()
    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='enroll', model_ids=["26_2"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='dev', purposes='probe', model_ids=["26_1"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='enroll', model_ids=["61_4"])
    nose.tools.eq_(len(objs), 1)
    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 61)
        nose.tools.eq_(obj.is_mirrored(), True)

    objs = db.objects(protocol=protocol, kinds='wrist', groups='eval', purposes='probe', model_ids=["61_4"])
    nose.tools.eq_(len(objs), 25*(4*2)*2)

def test_query_R_BEAT_1_protocol():
    db = Database()

    # dev:
    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="dev", kinds="wrist")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="dev", kinds="wrist")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes=["enroll"], groups="dev", kinds="wrist", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="dev", kinds="wrist", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes=["probe"], groups="dev", kinds="wrist", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="dev", kinds="wrist", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_1", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 8)

    # eval:
    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="eval", kinds="wrist")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="eval", kinds="wrist")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes=["enroll"], groups="eval", kinds="wrist", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="eval", kinds="wrist", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes=["probe"], groups="eval", kinds="wrist", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="eval", kinds="wrist", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_1", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 8)

    # test the same on PALMS:
    # dev:
    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes=["enroll"], groups="dev", kinds="palm", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="dev", kinds="palm", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes=["probe"], groups="dev", kinds="palm", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="dev", kinds="palm", model_ids=["1_1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_1", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 8)

    # eval:
    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_1", purposes=["enroll"], groups="eval", kinds="palm", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes="enroll", groups="eval", kinds="palm", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 1)

    objs = db.objects(protocol="R_BEAT_1", purposes=["probe"], groups="eval", kinds="palm", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_1", purposes="probe", groups="eval", kinds="palm", model_ids=["26_4"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_1", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 8)


def test_query_R_BEAT_4_protocol():
    db = Database()
    # dev:
    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="dev", kinds="wrist")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="dev", kinds="wrist")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["enroll"], groups="dev", kinds="wrist", model_ids=["1"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="dev", kinds="wrist", model_ids=["1"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["probe"], groups="dev", kinds="wrist", model_ids=["1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="dev", kinds="wrist", model_ids=["1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_4", groups="dev", kinds="palm")
    nose.tools.eq_(objs.sort(), ["1", "2"].sort())

    # eval:
    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="eval", kinds="wrist")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="eval", kinds="wrist")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["enroll"], groups="eval", kinds="wrist", model_ids=["26"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="eval", kinds="wrist", model_ids=["26"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["probe"], groups="eval", kinds="wrist", model_ids=["26"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="eval", kinds="wrist", model_ids=["26"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_4", groups="eval", kinds="palm")
    nose.tools.eq_(objs.sort(), ["26", "27"].sort())

    # test the same on PALMS:
    # dev:
    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="dev", kinds="palm")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["enroll"], groups="dev", kinds="palm", model_ids=["1"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="dev", kinds="palm", model_ids=["1"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["probe"], groups="dev", kinds="palm", model_ids=["1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="dev", kinds="palm", model_ids=["1"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_4", groups="dev", kinds="palm")
    nose.tools.eq_(objs.sort(), ["1", "2"].sort())

    # eval:
    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="eval", kinds="palm")
    nose.tools.eq_(len(objs), 2*2*4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["enroll"], groups="eval", kinds="palm", model_ids=["26"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes="enroll", groups="eval", kinds="palm", model_ids=["26"])
    nose.tools.eq_(len(objs), 4)

    objs = db.objects(protocol="R_BEAT_4", purposes=["probe"], groups="eval", kinds="palm", model_ids=["26"])
    nose.tools.eq_(len(objs), 16)

    objs = db.objects(protocol="R_BEAT_4", purposes="probe", groups="eval", kinds="palm", model_ids=["26"])
    nose.tools.eq_(len(objs), 16)

    objs = db.model_ids(protocol="R_BEAT_4", groups="eval", kinds="palm")
    nose.tools.eq_(objs.sort(), ["26", "27"].sort())


def test_dumplist():
  from bob.db.base.script.dbmanage import main
  nose.tools.eq_(main('putvein dumplist --protocol=L_4 --self-test'.split()), 0)


"""
import bob.db.putvein
from bob.db.putvein import Database
db = bob.db.putvein.Database()
import nose.tools
"""
