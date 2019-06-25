# -*- coding: utf-8 -*-

from kashgari.embeddings import BERTEmbedding
from kashgari.tasks.seq_labeling import BLSTMCRFModel
import os

os.environ['CUDA_VISIABLE_DEVICES'] = '0'

#embedding = BERTEmbedding("bert-base-chinese",200)
#将预训练模型载入进来
#model = BLSTMCRFModel(embedding)
#数据预处理
#model = BLSTMCRFModel.load_model('./ModelTest')

with open("C://Users//zhongbiao//Desktop//file//pk_bigadd_train.txt","rb") as f,\
     open("C://Users//zhongbiao//Desktop//file//ProduceFromUuidAdd_test.txt","rb") as validation:
     data = f.read().decode("utf-8")
     data2 = validation.read().decode("utf-8")
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
       
#得到训练集
        
validate_data = data2.split("\r\n")
word2=[]
label2=[]
word_set2=[]
label_set2=[]
#[[sentence],[...]...] 对应的label[[O,O,....],....]划分成一句一句训练
for i in validate_data:
    SP=i.split(' ')
    if(len(SP)==2):
        word2.append(SP[0])
        label2.append(SP[1])
    else:
        word_set2.append(word2)
        word2=[]
        label_set2.append(label2)
        label2=[]
#得到验证集
#开始训练


#model.fit(word_set,label_set,epochs=100,batch_size=256)
#model.save('./Model_original1')


model = BLSTMCRFModel.load_model('./Model_originalBIG3')
model.fit(word_set,label_set,epochs=10,batch_size=256)
model.save('./Model_originalBIGADD1')

model = BLSTMCRFModel.load_model('./Model_originalBIGADD1')
model.fit(word_set,label_set,epochs=10,batch_size=256)
model.save('./Model_originalBIGADD2')

model = BLSTMCRFModel.load_model('./Model_originalBIGADD2')
model.fit(word_set,label_set,epochs=10,batch_size=256)
model.save('./Model_originalBIGADD3')

model = BLSTMCRFModel.load_model('./Model_originalBIGADD3')
model.fit(word_set,label_set,epochs=10,batch_size=256)
model.save('./Model_originalBIGADD4')













