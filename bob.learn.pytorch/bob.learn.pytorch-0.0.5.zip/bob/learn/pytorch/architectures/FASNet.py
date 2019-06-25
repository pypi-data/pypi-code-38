import torch
from torch import nn
from torchvision import models


class FASNet(nn.Module):

	"""PyTorch Reimplementation of Lucena, Oeslle, et al. "Transfer learning using 
	convolutional neural networks for face anti-spoofing."
	International Conference Image Analysis and Recognition. Springer, Cham, 2017.
	Referenced from keras implementation: https://github.com/OeslleLucena/FASNet

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

	def __init__(self, pretrained=True):

		""" Init method

		Parameters
		----------
		pretrained: bool
			if set `True` loads the pretrained vgg16 model.

		"""
		super(FASNet, self).__init__()

		vgg = models.vgg16(pretrained=pretrained)

		features = list(vgg.features.children())

		self.enc = nn.Sequential(*features)

		self.linear1=nn.Linear(25088,256)

		self.relu=nn.ReLU()

		self.dropout= nn.Dropout(p=0.5)

		self.linear2=nn.Linear(256,1)

		self.sigmoid= nn.Sigmoid()


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

		x=enc.view(-1,25088)

		x=self.linear1(x)

		x=self.relu(x)

		x=self.dropout(x)

		x=self.linear2(x)

		x=self.sigmoid(x)  

		return x
