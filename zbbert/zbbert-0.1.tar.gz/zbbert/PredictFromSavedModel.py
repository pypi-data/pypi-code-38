# -*- coding: utf-8 -*-

from kashgari.tasks.seq_labeling import BLSTMCRFModel
from TextProcess import pause
new_model = BLSTMCRFModel.load_model('./ModelTest')
def textprocess(string):
    ReList=[]
    for i in string:
        ReList.append(i)
    return ReList
with open("C://Users//zhongbiao//Desktop//file//ProduceFromUuid_test.txt","rb") as f:
     data = f.read().decode("utf-8")
train_data = data.split("\r\n")
word=[]
label=[]
word_set=[]
label_set=[]
#[[sentence],[...]...] 对应的label[[O,O,....],....]划分成一句一句训练
for i in train_data:
    SP=i.split(' ')
    if(len(SP)==2):
        word.append(SP[0])
        label.append(SP[1])
    else:
        word_set.append(word)
        word=[]
        label_set.append(label)
        label=[]
new_model.evaluate(word_set,label_set)
#print(new_model.predict([a,b,c,d,e]))
