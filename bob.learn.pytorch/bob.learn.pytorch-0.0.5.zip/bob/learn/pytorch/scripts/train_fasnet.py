#!/usr/bin/env python
# encoding: utf-8


""" Train a FASNet for face PAD

Usage:
  %(prog)s <configuration> 
            [--model=<string>] [--batch-size=<int>] [--num-workers=<int>][--epochs=<int>] 
            [--learning-rate=<float>][--do-crossvalidation][--seed=<int>] 
            [--output-dir=<path>] [--use-gpu] [--verbose ...]

Arguments:
  <configuration>  A configuration file, defining the dataset and the network

Options:
  -h, --help                            Shows this help message and exits
      --model=<string>                  Filename of the model to load (if any). 
      --batch-size=<int>                Batch size [default: 64]
      --num-workers=<int>               Number subprocesses to use for data loading [default: 0]
      --epochs=<int>                    Number of training epochs [default: 20]
      --learning-rate=<float>           Learning rate [default: 0.01]
      --do-crossvalidation              Whether to perform cross validation [default: False]
  -S, --seed=<int>                      The random seed [default: 3] 
  -o, --output-dir=<path>               Dir to save stuff [default: training]
  -g, --use-gpu                         Use the GPU
  -v, --verbose                         Increase the verbosity (may appear multiple times).

Note that arguments provided directly by command-line will override the ones in the configuration file.

Example:

  To run the training process 

    $ %(prog)s config.py 

See '%(prog)s --help' for more information.

"""

import os, sys
import pkg_resources

import torch
import numpy
from docopt import docopt

import bob.core
logger = bob.core.log.setup("bob.learn.pytorch")

from bob.extension.config import load
from bob.learn.pytorch.trainers import FASNetTrainer
from bob.learn.pytorch.utils import get_parameter

version = pkg_resources.require('bob.learn.pytorch')[0].version

def main(user_input=None):
  
  # Parse the command-line arguments
  if user_input is not None:
      arguments = user_input
  else:
      arguments = sys.argv[1:]

  prog = os.path.basename(sys.argv[0])
  completions = dict(prog=prog, version=version,)
  args = docopt(__doc__ % completions,argv=arguments,version='Train a FASNet (%s)' % version,)

  # load configuration file
  configuration = load([os.path.join(args['<configuration>'])])
  
  # get the pre-trained model file, if any
  model = args['--model']
  if hasattr(configuration, 'model'):
    model = configuration.model
  
  # get various parameters, either from config file or command-line 
  batch_size = get_parameter(args, configuration, 'batch_size', 64)
  num_workers = get_parameter(args, configuration, 'num_workers', 0)
  epochs = get_parameter(args, configuration, 'epochs', 20)
  learning_rate = get_parameter(args, configuration, 'learning_rate', 0.01)
  seed = get_parameter(args, configuration, 'seed', 3)
  output_dir = get_parameter(args, configuration, 'output_dir', 'training')
  use_gpu = get_parameter(args, configuration, 'use_gpu', False)
  verbosity_level = get_parameter(args, configuration, 'verbose', 0)
  do_crossvalidation  = get_parameter(args, configuration, 'do_crossvalidation', False)
  
  bob.core.log.set_verbosity_level(logger, verbosity_level)
  bob.io.base.create_directories_safe(output_dir)

  # print parameters
  logger.debug("Model file = {}".format(model))
  logger.debug("Batch size = {}".format(batch_size))
  logger.debug("Num workers = {}".format(num_workers))
  logger.debug("Epochs = {}".format(epochs))
  logger.debug("Learning rate = {}".format(learning_rate))
  logger.debug("Seed = {}".format(seed))
  logger.debug("Output directory = {}".format(output_dir))
  logger.debug("Use GPU = {}".format(use_gpu))
  logger.debug("Perform cross validation = {}".format(do_crossvalidation))

  # process on the arguments / options
  torch.manual_seed(seed)
  if use_gpu:
    torch.cuda.manual_seed_all(seed)
  if torch.cuda.is_available() and not use_gpu:
    logger.warn("You have a CUDA device, so you should probably run with --use-gpu")

  # get data
  if hasattr(configuration, 'dataset'):
    
    dataloader={}

    if not do_crossvalidation:

      logger.info("There are {} training samples".format(len(configuration.dataset['train'])))

      dataloader['train'] = torch.utils.data.DataLoader(configuration.dataset['train'], batch_size=batch_size, num_workers=num_workers, shuffle=True)

    else:

      dataloader['train'] = torch.utils.data.DataLoader(configuration.dataset['train'], batch_size=batch_size, num_workers=num_workers, shuffle=True)
      dataloader['val'] = torch.utils.data.DataLoader(configuration.dataset['val'], batch_size=batch_size, num_workers=num_workers, shuffle=True)

      logger.info("There are {} training samples".format(len(configuration.dataset['train'])))
      logger.info("There are {} validation samples".format(len(configuration.dataset['val'])))
    
  else:
    logger.error("Please provide a dataset in your configuration file !")
    sys.exit()
  
  # train the network
  if hasattr(configuration, 'network'):
    trainer = FASNetTrainer(configuration.network, batch_size=batch_size, use_gpu=use_gpu, verbosity_level=verbosity_level,tf_logdir=output_dir+'/tf_logs',do_crossvalidation=do_crossvalidation)
    trainer.train(dataloader, n_epochs=epochs, learning_rate=learning_rate, output_dir=output_dir, model=model)
  else:
    logger.error("Please provide a network in your configuration file !")
    sys.exit()
