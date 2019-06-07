import torch
import logging
import tqdm
import copy
import time
import numpy as np
import random
from tensorboardX import SummaryWriter

from torch.nn import functional as F
from sklearn.metrics import average_precision_score

'''
TODO gym behavior should be change, it should have list of function to apply on any stage of training it will faciliate adding any addtional operation during training
'''

class GYM:
    def __init__(self,train,valid,model,metric,optimizer,loss,loss_ratios=[1],names=['Task'],device=torch.device('cuda:0'),cut_output=[False],logger=False):
        '''
        train,valid - represent data iterator for training and for validation, it should be torchtext Iterator if you want to provide dfferent iterator you should also change data_flow and workout methods
        model - model which you would like to work with (nn.Module)
        metric - class for computing metric should contain two @staticmethod - 'get_best' which will take best metric from list and 'evaluate' which will take lists of model outputs and true labels and compute metric
        optimizer - torch Optimizer
        loss - torch Loss 
        names - names of the task with which you want to train your model it could be None if you do not want to provide any
        device - torch device
        cut_output - sometimies it could be usefull to cut output only to prediction for ground true, especially when you train language model and you have prediction for great number of words
        '''
        self.logger = logger
        
        self.train = train if isinstance(train,list) else [train]
        self.valid = valid if isinstance(valid,list) else [valid]
        self.tasks = len(self.train)
        self.model_origin = model
        self.metric = metric if isinstance(metric,list) else [metric]
        if len(self.metric) != self.tasks:
            self.metric = [self.metric[0]] * self.tasks

        self.loss_ratios = loss_ratios
        if len(self.loss_ratios) != self.tasks:
            self.loss_ratios = [self.loss_ratios[0]] * self.tasks

        if len(names) == self.tasks:
            self.names = names
        else:
            self.names = ['Task' + i.__str__() for i in range(self.tasks)]
        self.optimizer = optimizer
        self.loss = loss
        self.device = device
        self.cut_output = cut_output if isinstance(cut_output,list) else [cut_output]
        if len(self.cut_output) != self.tasks:
            self.cut_output = [self.cut_output[0]] * self.tasks 

    def save_state(self,obj):
        '''
        this method simply checks if metric after validation is so far the best and if yes it will store copy of model state dict
        '''
        self.last_state_dict = copy.deepcopy(self.model.cpu().state_dict())
        self.optimizer_last_state_dict = copy.deepcopy(self.optimizer.state_dict())
        if self.metric[0].get_best(self.v_metrics[self.names[0]]) == self.v_metrics[self.names[0]][-1]:
            self.best_state_dict = copy.deepcopy(self.model.cpu().state_dict())
            self.optimizer_best_state_dict = copy.deepcopy(self.optimizer.state_dict())
        
        self.model.to(self.device)

    def init_optimizer(self,obj):
        self.optimizer.__init__(self.model.parameters(),**self.optimizer.defaults)

    def workout(self,check_interval=0,max_epochs=float('Inf'),stop_after_one=False,dynamic_loss=False,drop_last=False):
        '''
        check interval - after which number of iteration validation should be done, if check_interval==0 validation will be done after 1 epoch, if check_interval < 1 validation will be done after provided fraction of 1 epoch, if check_interval >= 1 validation will be done after provided number of iterations
        max_epoch - maximum number of epoch after which training will end
        stop_after_one - it will simply stop the trening after one interval
        dynamic_loss - if loss should be scaled based on evalutaion (will be taken out of gym in the future)
        drop_last - if batches of size 1 should be dropped
        '''
        self.drop_last = drop_last
        self.model = copy.deepcopy(self.model_origin).to(self.device)

        self.train_lens = [len(train) for train in self.train]
        self.train_len = self.train_lens[0]
        self.train_iters = [0] * len(self.train)
        self.time_start = time.time()

        self.start_log()
        self.init_optimizer(self)

        train_it = [iter(train) for train in self.train]

        if 0 < check_interval < 1:
            check_interval = int(self.train_len * check_interval)
        elif check_interval==0:
            check_interval = self.train_len
        self.intervals_in_epoch = self.train_len / check_interval
    
        while True:
            try:
                t_out, t_lab, t_loss = self.training(iterators=train_it,n_iters=check_interval)
                v_out, v_lab, v_loss = self.validation(iterators=[iter(valid) for valid in self.valid],lengths = [len(valid) for valid in self.valid])
                for t in range(self.tasks):
                    task_name = self.names[t]
                    t_metric = self.metric[t].evaluate(t_out[t], t_lab[t])
                    v_metric = self.metric[t].evaluate(v_out[t], v_lab[t])
                    self.log_metrics(t,t_metric,v_metric,t_loss[t],v_loss[t],task_name)
                    if dynamic_loss:
                        self.dynamic_loss(self,t_out[t], t_lab[t],v_out[t], v_lab[t])
                    
                self.save_state(self)
                if stop_after_one:
                    stopping_reason = 'Stop after one.'
                    break
                stop, reason = self.early_stopping(self)
                if stop:
                    stopping_reason = reason
                    break
                if self.train_iters[t]//self.train_lens[t] >= max_epochs:
                    stopping_reason = 'Max_epochs.'
                    break
            except KeyboardInterrupt:
                stopping_reason = 'KeyboardInterrupt.'
                break

        self.model.cpu()
        try:
            torch.cuda.empty_cache()
        except Exception as e:
            logging.error(e)
            logging.exception(e)
            pass

        results = {name:{'train_metrics':self.t_metrics[name],
                'valid_metrics':self.v_metrics[name],
                'train_losses':self.t_losses[name],
                'valid_losses':self.v_losses[name],
                'best_valid_metric':self.metric[i].get_best(self.v_metrics[name]), 
                'best_train_metric':self.metric[i].get_best(self.t_metrics[name])} for i,name in enumerate(self.names)}
        results['stopping_reason'] = stopping_reason
        return results
    
    def start_log(self):
        '''
        method which intiate logging, simply printing columns headers and printing format
        also it initiate metrics and losses list which will then store them
        '''
        self.t_metrics = {name: [] for name in self.names}
        self.v_metrics = {name: [] for name in self.names}
        self.t_losses = {name: [] for name in self.names}
        self.v_losses = {name: [] for name in self.names}
        self.log_template = ' '.join(
            '{:<12s},{:>6.0f},{:>5.0f},{:>9.0f},{:>5.0f}/{:<5.0f} {:>7.0f}%,{:>8.6f},{:8.6f},{:12.4f},{:12.4f}'.split(','))
        print(' '.join(
            '{:<12s},{:>6s},{:>5s},{:>9s},{:>10s}, {:>7s},{:>8s},{:14s},{:8s},{:2s}'.split(',')).format(
            'Name',
            'Time',
            'Epoch',
            'Iteration',
            'Progress',
            '(%Epoch)',
            'Loss',
            'Dev/Loss',
            'Metric',
            'Dev/Metric'
        ))
    def log_metrics(self,t,t_metric,v_metric,t_loss,v_loss,name):
        '''
        method which will log important statistic during traning and add intrvale metric and loss to lists
        '''

        self.t_metrics[name].append(t_metric)
        self.v_metrics[name].append(v_metric)
        self.t_losses[name].append(t_loss)
        self.v_losses[name].append(v_loss)
        to_print = self.log_template.format(name,time.time() - self.time_start,
                                       self.train_iters[t]//self.train_lens[t],
                                       self.train_iters[t], 
                                       self.train_iters[t]%self.train_lens[t],
                                       self.train_lens[t],
                                       100. * ((self.train_iters[t]%self.train_lens[t]) / self.train_lens[t]),
                                       t_loss,
                                       v_loss, 
                                       t_metric, 
                                       v_metric)
        if name == self.names[0] and len(self.names)>1:
            to_print = '\033[3m' + to_print + '\033[0m'
        
        print(to_print)
        
        if self.logger:
            self.logger.log_validation(t_metric, v_metric, v_loss,
                         self.train_iters[t])
        
    def training(self,iterators,n_iters):

        '''
        method which will do the trainig, update weights
        '''
        self.model.train()
        output_l = [[None] * n_iters for i in range(self.tasks)]
        labels_l = [[None] * n_iters for i in range(self.tasks)]
        loss_l = [[None] * n_iters for i in range(self.tasks)]
        with tqdm.tqdm(total=n_iters,leave=False,desc='Training') as pbar:
            for i in range(n_iters):
                self.optimizer_update(self)
                losses = 0
                for it, iterator in enumerate(iterators):
                    try:
                        data = next(iterator)
                    except:
                        iterators[it] = iter(self.train[it])
                        data = next(iterators[it])
                        
                    self.train_iters[it] += 1
                    output, labels, loss = self.data_flow(self,data,it)
                    if self.cut_output[it]:
                        output = self.cut_out(output,labels)
                    losses += loss * self.loss_ratios[it]
                    output_l[it][i], labels_l[it][i], loss_l[it][i] = output.detach().cpu(), labels.detach().cpu(), loss.item()
                
                if not isinstance(losses,int):
                    self.update(losses)
                pbar.set_postfix(grad_norm=self.norm,loss=loss.item(),)
                pbar.update(1)
                if self.logger:
                    self.logger.log_training(loss.item(),self.norm,self.train_iters[it],self.model)
                
        return [self.clear(out) for out in output_l], [self.clear(lab) for lab in labels_l], [sum(self.clear(loss))/len(self.clear(loss)) for loss in loss_l]

    def validation(self,iterators,lengths):
        '''
        method simply validate model on validation dataset
        '''
        self.model.eval()
        output_l = [[None]*length for length in lengths]
        labels_l = [[None]*length for length in lengths]
        loss_l = [[None]*length for length in lengths]
        for it, iterator in enumerate(iterators):
            for i in tqdm.tqdm(range(lengths[it]),leave=False,desc='Validation-'+self.names[it]):
                data = next(iterator)
                output, labels, loss = self.data_flow(self,data,it)
                if self.cut_output[it]:
                    output = self.cut_out(output,labels)
                output_l[it][i], labels_l[it][i], loss_l[it][i] = output.detach().cpu(), labels.detach().cpu(), loss.item()
        return [self.clear(out) for out in output_l], [self.clear(lab) for lab in labels_l], [sum(self.clear(loss))/len(self.clear(loss)) for loss in loss_l]
            
    def data_flow(self,obj,data,it):
        '''
        method which shows how data is inserting to model and how the loss is computing
        strongly depended on torchtext Iterator batch as data
        '''
        inputs, targets = data
        targets = targets.to(self.device)
        output = self.model(inputs.to(self.device),it)
        loss = self.loss(output,targets)
        return output, targets, loss
    
    def update(self,loss):
        '''
        post training iteration hook which will do beckpropagation, gredients and weight update
        '''
        self.optimizer.zero_grad()
        loss.backward()
        self.norm = self.gradients_clipping(self)
        self.optimizer.step() 

    def cut_out(self,output,labels):
        '''
        method to cut out useless prediction
        '''
        ls_out = -F.log_softmax(output,dim=-1)
        return ls_out.gather(1,labels.unsqueeze(1))
    
    def dynamic_loss(self,obj,t_out, t_lab,v_out, v_lab):
        '''
        method which computes overfitting of a model per label and base on that changes loss weights
        '''
        self.all_ap = []
        t_out = torch.cat(t_out)
        t_lab = torch.cat(t_lab)
        v_out = torch.cat(v_out)
        v_lab = torch.cat(v_lab)
        for i in range(t_out.size(1)):
            t_ap = average_precision_score(t_lab==i,t_out[:,i])
            v_ap = average_precision_score(v_lab==i,v_out[:,i])
            self.all_ap.append([t_ap,v_ap])
        diffs = []
        for aps in self.all_ap:
            diff = aps[1]/aps[0]
            diffs.append(diff)
        new_weights = F.softmax(torch.Tensor(diffs),dim=0)*t_out.size(1)
        self.loss.weight = new_weights.to(self.device)
        ### not sure if above work so to be sure I add line below
        self.loss.load_state_dict(self.loss.state_dict())

    def clear(self,l):
        '''
        remove None from list and return list
        '''
        return [e for e in l if e is not None]

    def optimizer_update(self,obj):
        '''
        if you want to change learnig rate bese on traning state here you can insert your function
        '''
        pass

    def early_stopping(self,obj):
        '''
        if you want to stop training base on its state you should put here your function
        if this method return True the training will stop
        '''
        return False, None
    
    def gradients_clipping(self,obj):
        '''
        method compute gradients norm which will be logged
        if you want to clip gradients you can put it here
        '''
        total_norm = 0
        parameters = self.model.parameters()
        parameters = list(filter(lambda p: p.grad is not None, parameters))
        for p in parameters:
            param_norm = p.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
        total_norm = total_norm ** (1. / 2)
        return total_norm

class Logger(SummaryWriter):
    def __init__(self,path):
        super(Logger,self).__init__(path)
    def log_training(self, loss, grad_norm,
                     iteration, model):
            self.add_scalar("grad.norm", grad_norm, iteration)
            self.add_scalar("training.loss", loss, iteration)
            
    def log_validation(self, t_metric, v_metric, v_loss,
                     iteration):
            self.add_scalar("training.metric", t_metric, iteration)
            self.add_scalar("validation.loss", v_loss, iteration)
            self.add_scalar("validation.metric", v_metric, iteration)
            for tag, value in model.named_parameters():
                tag = tag.replace('.', '/')
                self.add_histogram(tag, value.data.cpu().numpy(), iteration)