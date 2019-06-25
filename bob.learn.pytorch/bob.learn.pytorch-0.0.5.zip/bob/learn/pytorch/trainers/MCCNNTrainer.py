#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from bob.learn.pytorch.utils import comp_bce_loss_weights
from .tflog import Logger 

import bob.core
logger = bob.core.log.setup("bob.learn.pytorch")

import time
import os

import copy

class MCCNNTrainer(object):
	"""
	Class to train the MCCNN

	Attributes
	----------
	network: :py:class:`torch.nn.Module`
		The network to train
	batch_size: int
		The size of your minibatch
	use_gpu: bool
		If you would like to use the gpu
	verbosity_level: int
		The level of verbosity output to stdout
	
	"""
 
	def __init__(self, network, batch_size=64, use_gpu=False, adapted_layers='conv1-block1-group1-ffc',adapt_reference_channel=False, verbosity_level=2, tf_logdir='tf_logs',do_crossvalidation=False):
		""" Init function . The layers to be adapted in the network is selected and the gradients are set to `True` 
		for the  layers which needs to be adapted. 

		Parameters
		----------
		network: :py:class:`torch.nn.Module`
			The network to train
		batch_size: int
			The size of your minibatch
		use_gpu: bool
			If you would like to use the gpu
		adapted_layers: str
			The blocks in the CNN to adapt; only the ones listed are adapted in the training. The layers are separated by '-' in the
			string, for example 'conv1-block1-group1-ffc'. The fully connected layer in the output part are adapted always.
		adapt_reference_channel: bool
			If this value is `True` then 'ch_0' (which is the reference channel- usually, grayscale image) is also adapted. Otherwise the reference channel
			is not adapted, so that it can be used for Face recognition as well, default: `False`.
		verbosity_level: int
			The level of verbosity output to stdout
		do_crossvalidation: bool
			If set to `True`, performs validation in each epoch and stores the best model based on validation loss.

		"""
		self.network = network
		self.batch_size = batch_size
		self.use_gpu = use_gpu
		self.criterion = nn.BCELoss()
		self.do_crossvalidation=do_crossvalidation

		if self.do_crossvalidation:
			phases=['train','val']
		else:
			phases=['train']
		self.phases=phases

		if self.use_gpu:
			self.network.cuda()

		bob.core.log.set_verbosity_level(logger, verbosity_level)
		
		self.tf_logger = Logger(tf_logdir)

		layers_present = self.network.lcnn_layers.copy()

		layers_present.append('ffc')

		# select the layers in the network to adapt

		adapted_layers_list=adapted_layers.split('-')

		assert('ffc' in adapted_layers_list)

		assert(set(adapted_layers_list)<=set(layers_present)) # to ensure layer names are valid

		if adapt_reference_channel:# whether to adapt the color channel
			start_index = 0
		else:
			start_index = 1

		layers_to_adapt = ['linear1fc','linear2fc'] # Final fully connected layers are added in all cases

		#listing the layers which would be adapted 

		for i in range(start_index,self.network.num_channels):

			for layer in adapted_layers_list:
					if layer!='ffc':

					 layers_to_adapt.append("layer_dict.ch_{}_".format(i)+layer)

		layers_to_adapt = list(np.unique(layers_to_adapt))

		# Setting the gradients to true for the layers which needs to be adapted

		for name, param in  self.network.named_parameters():
			param.requires_grad = False
			for lta in layers_to_adapt:
				if lta in name:
					param.requires_grad = True

	def load_model(self, model_filename):
		"""Loads an existing model

		Parameters
		----------
		model_file: str
			The filename of the model to load

		Returns
		-------
		start_epoch: int
			The epoch to start with
		start_iteration: int
			The iteration to start with
		losses: list(float)
			The list of losses from previous training 
		
		"""
		
		cp = torch.load(model_filename)
		self.network.load_state_dict(cp['state_dict'])
		start_epoch = cp['epoch']
		start_iter = cp['iteration']
		losses = cp['loss']
		return start_epoch, start_iter, losses


	def save_model(self, output_dir, epoch=0, iteration=0, losses=None):
		"""Save the trained network

		Parameters
		----------
		output_dir: str
			The directory to write the models to
		epoch: int
			the current epoch
		iteration: int
			the current (last) iteration
		losses: list(float)
				The list of losses since the beginning of training 
		
		""" 
		
		saved_filename = 'model_{}_{}.pth'.format(epoch, iteration)    
		saved_path = os.path.join(output_dir, saved_filename)    
		logger.info('Saving model to {}'.format(saved_path))
		cp = {'epoch': epoch, 
					'iteration': iteration,
					'loss': losses, 
					'state_dict': self.network.cpu().state_dict()
					}
		torch.save(cp, saved_path)
		
		# moved the model back to GPU if needed
		if self.use_gpu :

			self.network.cuda()


	def train(self, dataloader, n_epochs=25, learning_rate=1e-4, output_dir='out', model=None):
		"""Performs the training.

		Parameters
		----------
		dataloader: :py:class:`torch.utils.data.DataLoader`
			The dataloader for your data
		n_epochs: int
			The number of epochs you would like to train for
		learning_rate: float
			The learning rate for Adam optimizer.
		output_dir: str
			The directory where you would like to save models 
		model: str
			The path to a pretrained model file to start training from; this is the PAD model; not the LightCNN model

		"""

		# if model exists, load it
		if model is not None:
			start_epoch, start_iter, losses = self.load_model(model)
			logger.info('Starting training at epoch {}, iteration {} - last loss value is {}'.format(start_epoch, start_iter, losses[-1]))
		else:
			start_epoch = 0
			start_iter = 0
			losses = []
			logger.info('Starting training from scratch')

		logger.info("Number of channels: {}".format(self.network.num_channels))

		for name, param in  self.network.named_parameters():

			if param.requires_grad == True:
				logger.info('Layer to be adapted from grad check : {}'.format(name))

		# setup optimizer

		optimizer = optim.Adam(filter(lambda p: p.requires_grad, self.network.parameters()),lr = learning_rate )

		self.network.train(True)

		
		best_model_wts = copy.deepcopy(self.network.state_dict())
			
		best_loss = float("inf")

		# let's go
		for epoch in range(start_epoch, n_epochs):
			
			# in the epoch

			train_loss_history=[]

			val_loss_history = []

			for phase in self.phases:

				if phase == 'train':
					self.network.train()  # Set model to training mode
				else:
					self.network.eval()   # Set model to evaluate mode

				for i, data in enumerate(dataloader[phase], 0):

		 
					if i >= start_iter:
					
						start = time.time()
						
						img, labels = data

						labels=labels.float().unsqueeze(1)

						weights=comp_bce_loss_weights(labels)

						batch_size = len(img)

						if self.use_gpu:
							img = img.cuda()
							labels = labels.cuda()
							weights = weights.cuda()

						imagesv = Variable(img)
						labelsv = Variable(labels)
						
						# weights for samples, should help with data imbalance
						self.criterion.weight = weights

						optimizer.zero_grad()

						with torch.set_grad_enabled(phase == 'train'):

							output= self.network(imagesv)
							loss = self.criterion(output, labelsv)

							if phase == 'train':
								loss.backward()
								optimizer.step()
								train_loss_history.append(loss.item())								
							else:
								val_loss_history.append(loss.item())


						end = time.time()
						logger.info("[{}/{}][{}/{}] => Loss = {} (time spent: {}), Phase {}".format(epoch, n_epochs, i, len(dataloader[phase]), loss.item(), (end-start),phase))
						losses.append(loss.item())

						
			epoch_train_loss=np.mean(train_loss_history)

			logger.info("Train Loss : {}  epoch : {}".format(epoch_train_loss,epoch))

			if self.do_crossvalidation:

				epoch_val_loss=np.mean(val_loss_history)

				logger.info("Val Loss : {}  epoch : {}".format(epoch_val_loss,epoch))
				
				if phase == 'val' and epoch_val_loss < best_loss:

					logger.debug("New val loss : {} is better than old: {}, copying over the new weights".format(epoch_val_loss,best_loss))
					
					best_loss = epoch_val_loss
					best_model_wts = copy.deepcopy(self.network.state_dict())
		

			########################################  <Logging> ###################################
			if self.do_crossvalidation:
				info = {'train_loss':epoch_train_loss,'val_loss':epoch_val_loss}
			else:
				info = {'train_loss':epoch_train_loss}
			
			# scalar logs
			
			for tag, value in info.items():
				self.tf_logger.scalar_summary(tag, value, epoch+1)

			# Log values and gradients of the parameters (histogram summary)

			for tag, value in self.network.named_parameters():
				tag = tag.replace('.', '/')        
				try:          
					self.tf_logger.histo_summary(tag, value.data.cpu().numpy(), epoch+1)
					self.tf_logger.histo_summary(tag+'/grad', value.grad.data.cpu().numpy(), epoch+1)
				except:
					pass

			# Log images
			logimg=img.view(-1,img.size()[1]*128, 128)[:10].cpu().numpy()

			info = { 'images': logimg}    

			for tag, images in info.items():
				self.tf_logger.image_summary(tag, images, epoch+1)

			########################################  </Logging>  ###################################  
			
			
			# do stuff - like saving models
			logger.info("EPOCH {} DONE".format(epoch+1))

			self.save_model(output_dir, epoch=(epoch+1), iteration=0, losses=losses)
			  
		## load the best weights

		self.network.load_state_dict(best_model_wts)

		# best epoch is named as 100

		self.save_model(output_dir, epoch=100, iteration=0, losses=losses)
