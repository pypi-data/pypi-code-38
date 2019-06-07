import torch
from sklearn.metrics import roc_auc_score

'''
metric classes should always have at least two static methods 
`get_best` which takes list of metrics and return best metric
`evaluate` which takes list of labels and model predictions per batch and evaluate metric
'''

class Perplexity:
    @staticmethod
    def get_best(metrics):
        return min(metrics)

    @staticmethod
    def evaluate(out,lab):
        loss = torch.cat(out)
        return (loss.sum()/loss.size(0)).exp().item()

class Accuracy:
    @staticmethod
    def get_best(metrics):
        return max(metrics)
    
    @staticmethod
    def evaluate(out,lab):
        out = torch.cat(out)
        lab = torch.cat(lab)
        out_max = out.argmax(dim=1)
        score = out_max == lab
        return score.float().mean().item()

class ROC_AUC:
    @staticmethod
    def get_best(metrics):
        return max(metrics)
    
    @staticmethod
    def evaluate(out,lab):
        out = torch.cat(out)
        lab = torch.cat(lab)
        return roc_auc_score(lab, out[:, 1])

