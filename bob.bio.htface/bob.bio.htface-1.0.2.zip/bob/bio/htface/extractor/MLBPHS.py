#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.ip.base
import numpy
import math

from bob.bio.base.extractor import Extractor

class MLBPHS (Extractor):
    """
    Extracts block based multiscale LBP Histogram sequence.
    
    **Parameters**
      block_size: int
        Window size
        
      block_overlap: tuple
        Window overlap

      lbp_radius: list
         A list of LBP radius
      
      lbp_neighbor_count: int
        Number of LBP bins

      lbp_uniform: bool
        Uses uniform patterns?
        
      lbp_circular: bool
        Circular neighbourhood
      
      lbp_rotation_invariant: bool
        Rotation Invariant LBP?
      
      lbp_compare_to_average: bool
        Is the reference bin the average? If False, the pixel in the center will be the reference.

      lbp_add_average: bool
        Add average

      sparse_histogram: bool
      split_histogram:
    
    """

    def __init__(
        self,
        # Block setup
        block_size,    # one or two parameters for block size
        block_overlap = (0,0), # one or two parameters for block overlap
        # LBP parameters
        lbp_radius = [2],
        lbp_neighbor_count = 8,
        lbp_uniform = True,
        lbp_circular = True,
        lbp_rotation_invariant = False,
        lbp_compare_to_average = False,
        lbp_add_average = False,
        # histogram options
        sparse_histogram = False,
        split_histogram = None,
        get_histograms_per_block = False,
        variance_flooring = 10e-5
    ):
      """Initializes the local Gabor binary pattern histogram sequence tool chain with the given file selector object"""

      # call base class constructor
      Extractor.__init__(
          self,

          block_size = block_size,
          block_overlap = block_overlap,
          lbp_radius = lbp_radius,
          lbp_neighbor_count = lbp_neighbor_count,
          lbp_uniform = lbp_uniform,
          lbp_circular = lbp_circular,
          lbp_rotation_invariant = lbp_rotation_invariant,
          lbp_compare_to_average = lbp_compare_to_average,
          lbp_add_average = lbp_add_average,
          sparse_histogram = sparse_histogram,
          split_histogram = split_histogram,
          variance_flooring=variance_flooring
          
      )
      
      if not isinstance(lbp_radius, list):
          raise ValueError("Expected a `list` for `lbp_radius`")
      
      if len(lbp_radius) < 1:
          raise ValueError("It is necessary to have at least one radius set. {0} was set.".format(lbp_radius))

      self.m_lbp = []
      for r in lbp_radius:
          self.m_lbp.append(bob.ip.base.LBP (lbp_neighbor_count, radius=r, to_average=lbp_add_average, uniform=lbp_uniform, rotation_invariant=lbp_rotation_invariant))

      self.block_size=block_size
      self.block_overlap = block_overlap
      self.lbp_radius = lbp_radius
      self.get_histograms_per_block = get_histograms_per_block
      self.variance_flooring = variance_flooring
      

    def __call__(self, image):
        """Extracts the local binary pattern histogram sequence from the given image"""
        
        if image.ndim == 2:        

            if self.get_histograms_per_block:
                
                for l in self.m_lbp:
                    lbp_image = l(image)
                    blocks = bob.ip.base.block(lbp_image, self.block_size, self.block_overlap)
                    hist_blocks = []
                    
                    for i in range(blocks.shape[0]):
                        for j in range(blocks.shape[1]):
                            hist_blocks.append(bob.ip.base.histogram(blocks[i,j,:,:], l.max_label))

                hist_blocks = numpy.array(hist_blocks)
                hist_blocks = (hist_blocks - numpy.mean(hist_blocks, axis=0)) / numpy.std(hist_blocks, axis=0)
                hist_blocks = numpy.nan_to_num(hist_blocks, self.variance_flooring)
                
                            
                return hist_blocks
            else:
                
                histogram_shape = numpy.prod(bob.ip.base.lbphs_output_shape(image, self.m_lbp[0], self.block_size, self.block_overlap))* len(self.lbp_radius)
                hist = numpy.zeros((histogram_shape))
                
                offset = 0
                for l in self.m_lbp:
                    h = bob.ip.base.lbphs(image, l, block_size=self.block_size, block_overlap=self.block_overlap).flatten().astype('float')
                    hist[offset:offset+h.shape[0]] = h
                    offset += h.shape[0]
                    
                return hist

        else:
            hist_per_channel = []
            for i in range(image.shape[0]):
                
                channel_image = image[i, :, :]
                
            
                histogram_shape = numpy.prod(bob.ip.base.lbphs_output_shape(channel_image, self.m_lbp[0], self.block_size, self.block_overlap))* len(self.lbp_radius)
                hist = numpy.zeros((histogram_shape))
                
                offset = 0
                for l in self.m_lbp:
                    h = bob.ip.base.lbphs(channel_image, l, block_size=self.block_size, block_overlap=self.block_overlap).flatten().astype('float')
                    hist[offset:offset+h.shape[0]] = h
                    offset += h.shape[0]
                hist_per_channel += list(hist)
                
            return numpy.array(hist_per_channel)

