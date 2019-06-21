#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.io.base
import bob.io.image
import bob.ip.base
import numpy
from bob.extension.scripts.click_helper import verbosity_option, ResourceOption
import click


# YES, THOSE PARAMETERS ARE HARD-CODED.
# LEAVE ME ALONE
block_size    = 12
block_overlap = 8
pixels_white = 2


@click.command(context_settings={'ignore_unknown_options': True,
                                 'allow_extra_args': True})
@click.argument('input_path', required=True)
@click.argument('output_path', required=True)
def create_block_image(input_path, output_path, **kwargs):
    """
    This click command generates as block based image
    """

    img    = bob.io.base.load(input_path)
    shape  = bob.ip.base.block_output_shape(img, (block_size,block_size), (block_overlap,block_overlap))
    block_img = numpy.zeros(shape=shape)

    bob.ip.base.block(img, (block_size,block_size), (block_overlap,block_overlap), block_img)
    block_img = numpy.array(block_img, dtype='uint8')

    white_lines = (pixels_white*(block_img.shape[0]-1),pixels_white*(block_img.shape[1]-1))
    #print white_lines

    shape_big_image = (white_lines[0]+ block_img.shape[0]*block_img.shape[2], white_lines[1]+block_img.shape[1]*block_img.shape[3])
    big_image = 255*numpy.ones(shape=shape_big_image, dtype='uint8')

    offset_x = 0
    offset_y = 0

    for i in range(block_img.shape[1]):
      for j in range(block_img.shape[0]):
        big_image[offset_x:offset_x+block_img.shape[2], offset_y:offset_y+block_img.shape[3]] = block_img[j,i,:,:]
        offset_x += block_img.shape[2] + pixels_white

      #print offset_x
      offset_x = 0
      offset_y += block_img.shape[3] + pixels_white
      
    bob.io.base.save(big_image,output_path)
    bob.io.base.save(img.astype("uint8"),output_path + "_normal.jpg")

