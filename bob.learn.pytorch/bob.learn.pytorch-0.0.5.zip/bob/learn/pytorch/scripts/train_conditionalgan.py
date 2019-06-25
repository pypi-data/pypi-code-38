#!/usr/bin/env python
# encoding: utf-8
#!/usr/bin/env python
# encoding: utf-8

""" Train a Conditional GAN 

Usage:
  %(prog)s <configuration> 
           [--noise-dim=<int>] [--conditional-dim=<int>] 
           [--batch-size=<int>] [--epochs=<int>] [--sample=<int>]
           [--output-dir=<path>] [--use-gpu] [--seed=<int>] [--verbose ...]

Arguments:
  <configuration>  A configuration file, defining the dataset and the network

Options:
  -h, --help                    Show this screen.
  -V, --version                 Show version.
  -n, --noise-dim=<int>         The dimension of the noise [default: 100]
  -c, --conditional-dim=<int>   The dimension of the conditional variable [default: 13]
  -b, --batch-size=<int>        The size of your mini-batch [default: 64]
  -e, --epochs=<int>            The number of training epochs [default: 100] 
  -s, --sample=<int>            Save generated images at every 'sample' batch iteration [default: 1e10] 
  -o, --output-dir=<path>       Dir to save the logs, models and images [default: ./conditionalgan/] 
  -g, --use-gpu                 Use the GPU 
  -S, --seed=<int>              The random seed [default: 3] 
  -v, --verbose                 Increase the verbosity (may appear multiple times).

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

import bob.io.base
from bob.extension.config import load
from bob.learn.pytorch.trainers import ConditionalGANTrainer
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
  args = docopt(__doc__ % completions,argv=arguments,version='Train conditional GAN (%s)' % version,)

  # load configuration file
  configuration = load([os.path.join(args['<configuration>'])])
  
  # get various parameters, either from config file or command-line 
  noise_dim = get_parameter(args, configuration, 'noise_dim', 100)
  conditional_dim = get_parameter(args, configuration, 'conditional_dim', 13)
  batch_size = get_parameter(args, configuration, 'batch_size', 64)
  epochs = get_parameter(args, configuration, 'epochs', 20)
  sample = get_parameter(args, configuration, 'sample', 1e10)
  seed = get_parameter(args, configuration, 'seed', 3)
  output_dir = get_parameter(args, configuration, 'output_dir', 'training')
  use_gpu = get_parameter(args, configuration, 'use_gpu', False)
  verbosity_level = get_parameter(args, configuration, 'verbose', 0)

  bob.core.log.set_verbosity_level(logger, verbosity_level)
  images_dir = os.path.join(output_dir, 'samples')
  log_dir = os.path.join(output_dir, 'logs')
  model_dir = os.path.join(output_dir, 'models')
  bob.io.base.create_directories_safe(images_dir)
  bob.io.base.create_directories_safe(log_dir)
  bob.io.base.create_directories_safe(images_dir)

  # print parameters
  logger.debug("Noise dimension = {}".format(noise_dim))
  logger.debug("Conditional dimension = {}".format(conditional_dim))
  logger.debug("Batch size = {}".format(batch_size))
  logger.debug("Epochs = {}".format(epochs))
  logger.debug("Sample = {}".format(sample))
  logger.debug("Seed = {}".format(seed))
  logger.debug("Output directory = {}".format(output_dir))
  logger.debug("Use GPU = {}".format(use_gpu))
  
  # process on the arguments / options
  torch.manual_seed(seed)
  if use_gpu:
    torch.cuda.manual_seed_all(seed)
  if torch.cuda.is_available() and not use_gpu:
    logger.warn("You have a CUDA device, so you should probably run with --use-gpu")

   # get data
  if hasattr(configuration, 'dataset'):
    dataloader = torch.utils.data.DataLoader(configuration.dataset, batch_size=batch_size, shuffle=True)
    logger.info("There are {} training images".format(len(configuration.dataset)))
  else:
    logger.error("Please provide a dataset in your configuration file !")
    sys.exit()
  
  # train the model
  if hasattr(configuration, 'generator') and hasattr(configuration, 'discriminator'):
    trainer = ConditionalGANTrainer(configuration.generator, configuration.discriminator, [3, 64, 64], batch_size=batch_size, noise_dim=noise_dim, conditional_dim=conditional_dim, use_gpu=use_gpu, verbosity_level=verbosity_level)
    trainer.train(dataloader, n_epochs=epochs, output_dir=output_dir)
  else:
    logger.error("Please provide both a generator and a discriminator in your configuration file !")
    sys.exit()
