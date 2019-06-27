import numpy as np
import pandas as pd

from torch import nn

from tqdm import tqdm
tqdm.pandas()

from sklearn.neighbors import NearestNeighbors 

'''
ErrorAnalysis in beta version, strongly dependent on trochtext Iterator and can only work if dataset has only one field with text
'''

class ErrorAnalysis:
    def __init__(self, gym, join_pattern=' '):
        self.gym = gym
        batch_size = self.gym.valid.batch_size
        batch_size_fn = self.gym.valid.batch_size_fn
        self.gym.valid.batch_size = 1
        self.gym.valid.batch_size_fn = None
        if not hasattr(self.gym, 'model'):
            self.gym.model = self.gym.model_origin
        
        self.gym.model.to(gym.device)
        self.vactors = None
        valid_len = len(self.gym.valid)
        text_l = [None] * valid_len
        score_l = [None] * valid_len
        loss_l = [None] * valid_len
        preds_l = [None] * valid_len
        true_l = [None] * valid_len
        for i, data in enumerate(tqdm(self.gym.valid)):
            out,lab,loss = self.gym.data_flow(self.gym,data)
            loss_l[i] = loss.item()
            score_l[i] = self.gym.metric.evaluate([out],[lab])
            preds_l[i] = dict(zip(data.dataset.fields[data.target_fields[0]].vocab.itos,nn.functional.softmax(out,dim=-1).detach().cpu().numpy()[0]))
            true_l[i] = data.dataset.fields[data.target_fields[0]].vocab.itos[lab.item()]
            t,_=data
            new_text = join_pattern.join([data.dataset.fields[data.input_fields[0]].vocab.itos[i.item()] for i in t[0]])
            text_l[i] = new_text
                 
        self.error_tab = pd.DataFrame({'text':text_l,'label':true_l,'preds':preds_l,'loss':loss_l,'score':score_l}).sort_values('loss',ascending=False).reset_index(drop=True)
        self.field = data.dataset.fields[data.input_fields[0]]
        
        self.gym.valid.batch_size = batch_size
        self.gym.valid.batch_size_fn = batch_size_fn
        
    def create_embeddings(self,embeddings=None):
        if embeddings is None:
            emb_present = False
            for m in self.gym.model.modules():
                if isinstance(m,nn.Embedding) and m.num_embeddings==len(self.field.vocab.itos):
                    embeddings = m
                    emb_present = True
            if not emb_present:
                raise ValueError('Cannot find embeddings.')
        self.embeddings = embeddings
        self.error_tab['vec_rep'] = self.error_tab['text'].progress_apply(lambda x: self.embeddings(self.field.process([x]).to(self.gym.device)[0]).sum(dim=0).detach().cpu())
        self.nn_estimator = NearestNeighbors()
        self.nn_estimator.fit(np.stack(self.error_tab['vec_rep'].values))
        
    def find_nn(self,text=None,index=None,n=5,verbose=True):
        if index is not None:
            idx = self.nn_estimator.kneighbors(self.error_tab['vec_rep'][index].reshape(1, -1),n,return_distance=False)
        elif text is not None:
            vector = self.embeddings(self.field.process([text])[0]).sum(dim=0).detach().cpu()
            idx = self.nn_estimator.kneighbors(vector.reshape(1, -1),n,return_distance=False)
        else:
            raise ValueError('Text or index has to be provided.')
        if verbose:
            for index, row in self.error_tab.loc[idx.tolist()[0]].iterrows():
                print(row.score)
                print(row.loss)
                print(row.preds)
                print(row.label)
                print(row.text)
        return self.error_tab[['text','label','preds','loss','score']].loc[idx.tolist()[0]]
            
        
    