#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
from cacherUtils import FMQLReplyStore, zipAllReplies

def a():

    replyStore = FMQLReplyStore("/data/vista/999/Data/")
    flTyp = "3_081"
    iter = replyStore.iterator(onlyTypes=[flTyp])
    for flJSON in iter.next():
        print "First", len(flJSON["results"])
        print "\t", flJSON["fmql"]
        print "\t", flJSON["queryCached"]
        print
        break
    lastReplyOfType = replyStore.lastReplyOfType(flTyp)
    print "Last Reply of Type", len(lastReplyOfType["results"]), lastReplyOfType["fmql"], lastReplyOfType.keys()
    print "Last result of last reply", json.dumps(lastReplyOfType["results"][-1], indent=4)

a()

def b():
    dir = "tmp/"
    zipAllReplies(dir)

# b()





