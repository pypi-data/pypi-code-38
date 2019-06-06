#-*- coding: utf-8 -*-
import xmind
from xmind.core import workbook,saver
from xmind.core.topic import TopicElement

w = xmind.load("test.xmind") # load an existing file or create a new workbook if nothing is found
w = xmind.load(u"mac.xmind")
s1=w.getPrimarySheet() # get the first sheet
# print(s1.getTitle())
r1=s1.getRootTopic() # get the root topic of this sheet
topics_l01 = r1.getSubTopics() 
for topic_case_group in topics_l01:
    topic_case_priority_name = topic_case_group.getMarkers()[0].getMarkerId() # # case priority
    print(topic_case_priority_name)
    pass