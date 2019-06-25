import torch
from torch import nn
from torchvision import models
import numpy as np


class DeepMSPAD(nn.Module):

	""" Deep multispectral PAD algorithm

	The initialization uses `Cross modality pre-training` idea from the following paper:

	Wang L, Xiong Y, Wang Z, Qiao Y, Lin D, Tang X, Van Gool L. Temporal segment networks: 
	Towards good practices for deep action recognition. InEuropean conference on computer 
	vision 2016 Oct 8 (pp. 20-36). Springer, Cham.


	Attributes:
		pretrained: bool
			if set `True` loads the pretrained vgg16 model. 
		vgg: :py:class:`torch.nn.Module`
			The VGG16 model
		relu: :py:class:`torch.nn.Module`
			ReLU activation
		enc: :py:class:`torch.nn.Module`
			Uses the layers for feature extraction
		linear1: :py:class:`torch.nn.Module`
			Fully connected layer
		linear2: :py:class:`torch.nn.Module`
			Fully connected layer
		dropout: :py:class:`torch.nn.Module`
			Dropout layer
		sigmoid: :py:class:`torch.nn.Module`
			Sigmoid activation
	"""

	def __init__(self, pretrained=True, num_channels=4):

		""" Init method

		Parameters
		----------
		pretrained: bool
			if set `True` loads the pretrained vgg16 model.
		num_channels: int
			Number of channels in the input

		"""
		super(DeepMSPAD, self).__init__()

		vgg = models.vgg16(pretrained=pretrained)

		features = list(vgg.features.children())

		# temp layer to extract weights
		temp_layer = features[0]  

		# Implements ``Cross modality pre-training``

		# Mean of weight and bias for all filters
		bias_values = temp_layer.bias.data.detach().numpy()
		mean_weight = np.mean(temp_layer.weight.data.detach().numpy(),axis=1) # for 64 filters

		new_weight = np.zeros((64,num_channels,3,3))

		for i in range(num_channels):
			new_weight[:,i,:,:]=mean_weight


		# initialize new layer with required number of channels `num_channels`

		features[0] = nn.Conv2d(num_channels, 64, kernel_size=(3, 3), stride=(1, 1), padding =(1, 1))

		features[0].weight.data = torch.Tensor(new_weight)

		features[0].bias.data = torch.Tensor(bias_values) #check

		self.enc = nn.Sequential(*features)

		self.linear1 = nn.Linear(25088,256)

		self.relu = nn.ReLU()

		self.dropout = nn.Dropout(p=0.5)

		self.linear2 = nn.Linear(256,1)

		self.sigmoid = nn.Sigmoid()


	def forward(self, x):
		""" Propagate data through the network

		Parameters
		----------
		x: :py:class:`torch.Tensor` 
		  The data to forward through the network

		Returns
		-------
		x: :py:class:`torch.Tensor` 
		  The last layer of the network
		
		"""
	   
		enc = self.enc(x)

		x = enc.view(-1,25088)

		x = self.linear1(x)

		x = self.relu(x)

		x = self.dropout(x)

		x = self.linear2(x)

		x = self.sigmoid(x)  

		return x
