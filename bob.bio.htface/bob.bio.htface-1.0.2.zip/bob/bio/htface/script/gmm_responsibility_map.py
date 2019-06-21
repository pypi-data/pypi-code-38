#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Wed 06 Jan 2016 10:47:02 CET 

"""
This is an awesome tool.

Computes the GMM responsibility map of a parts-based face recognition sytem over a training set of a given database
Will be computed one image per gaussian, per modality, so be carefull with the UBM selection

"""

import os
import sys
import argparse
import numpy

import bob.learn.em
import bob.io.base
import bob.io.image
import bob.ip.base
import bob.bio.base


def resize(img, scale, img_final_size):
  output = numpy.zeros(shape=img_final_size)
  bob.ip.base.GeomNorm(0,scale,(56,46),(0,0))(img, output, (0,0))

  return output

def norm_image(img):
  min = numpy.min(img)
  max = numpy.max(img)

  return (img-min) * ((255-0)/(max-min)) + 0

def znorm(f):
  return (f-numpy.mean(f,axis=0))/numpy.std(f,axis=0)


def block_image(img, block_size, block_overlap, hitted_responsabilities):
  """
   Computes the heat map
  """
  
  #import ipdb; ipdb.set_trace();
  colors = abs(255-norm_image(hitted_responsabilities))

  pixels_white = 2

  block_img  = bob.ip.base.block(img, block_size, block_overlap)
  white_lines = (pixels_white*(len(block_img)-1), pixels_white*(len(block_img[0])-1))

  shape_big_image = ( white_lines[0]+ len(block_img) * block_size[0],  white_lines[1] + len(block_img[0]) * block_size[1])
  big_image = 255*numpy.ones(shape=shape_big_image, dtype='uint8')

  offset_x = 0
  offset_y = 0

  for i in range(len(block_img)):
    for j in range(len(block_img[i])):

      element = i * len(block_img[i]) + j

      #if element in hitted_responsabilities:
      big_image[offset_x:offset_x + block_size[0], offset_y:offset_y + block_size[1]] = numpy.ones(shape=(block_size[0], block_size[1]))*colors[element]

        #big_image[offset_x:offset_x+block_img.shape[2], offset_y:offset_y+block_img.shape[3]] = block_img[j,i,:,:]

      offset_y += block_size[0] + pixels_white

    #print offset_x
    offset_y  = 0
    offset_x += block_size[1] + pixels_white

  return big_image



def main():

  RESOURCE_KEY = "database"
  databases = bob.bio.base.utils.resources.resource_keys(RESOURCE_KEY)

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('ubm', default='', help='UBM File')
  
  parser.add_argument('features_dir', default='', help='Feature directory')

  parser.add_argument('output', default='', help='Output directory. Be carefull with the number of gaussians of your UBM, will be generated one image per gaussian per modality.')

  parser.add_argument('--image-size', nargs=2, type=int, default=[80,64], help='Image size. Default to %(default)s')
  
  parser.add_argument('--block-size', nargs=2, type=int,default=[12,12], help='Size of each block (parts based recognition system). Default to %(default)s')
  
  parser.add_argument('--block-overlap', nargs=2, type=int, default=[11,11], help='Size of the block overlap (parts based recognition system). Default to %(default)s')
  
  parser.add_argument('--database', default=databases[0], choices=databases, help='Database to be used. Default to %(default)s', required = True)
  
  parser.add_argument('--protocol', default="", help='Database protocol. Please check the database documentation for more information.', required = True)
  
  parser.add_argument('--modalities', nargs=2, default=['photo', 'sketch'], help='Database modalities. Default to %(default)s .', required = True)
    

  args = parser.parse_args()

  
  try:
    ubm   = bob.learn.em.GMMMachine(bob.io.base.HDF5File(args.ubm))
  except RuntimeError:
    hdf5 = bob.io.base.HDF5File(args.ubm)
    hdf5.cd('Projector')
    ubm   = bob.learn.em.GMMMachine(hdf5)

  ubm_components = ubm.shape[0]  

  if not os.path.exists(args.output):
    bob.io.base.create_directories_safe(args.output)
  
  database = bob.bio.base.utils.resources.load_resource(args.database, RESOURCE_KEY)
  #data     = database.training_files(protocol=args.protocol)[0:100]
  data     = database.objects(protocol=args.protocol, group="world")

  sys.stdout.write("Training set size {0}\n".format(len(data))); sys.stdout.flush();
  
  hitted_blocks_per_modality =  []#Lists that will hold the responsibilities
  
  img = numpy.zeros(shape=args.image_size)  

  for m in args.modalities:
  
    sys.stdout.write("\nProcessing {0}: ".format(m)); sys.stdout.flush();
        
    bob.io.base.create_directories_safe(os.path.join(args.output,m))
    #for c in range(ubm.shape[0]):
    #print "Ploting component {0}".format(c)
    
    shape = bob.ip.base.block_output_shape(img , args.block_size, args.block_overlap)

    hitted_blocks = numpy.zeros(shape=(ubm_components, shape[0] * shape[1]))
    for d in data:
    
      sys.stdout.write('.'); sys.stdout.flush();
      
      #####
      # MOST IMPORTANT THING OF THE SCRIPT. Filtering the modalities
      #####
      if d.f.modality != m:
        continue
      
      features = bob.io.base.load(os.path.join(args.features_dir,d.path+".hdf5"))

        #for each block, computes the responsibilities
      for i in range(len(features)):
        f = features[i,:]
        stats = bob.learn.em.GMMStats(ubm.shape[0], ubm.shape[1])
        ubm.acc_statistics(f, stats)
        responsability = numpy.argsort(stats.n)[-1]

          #if responsability==c:
            #hitted_blocks[i]+=1
            
        hitted_blocks[responsability,i]+=1

      #hitted_blocks_per_modality[modality_index].append(hitted_blocks)
    hitted_blocks_per_modality.append(hitted_blocks)
    #modality_index+=1

  
  #Now, for each component we have to normalize the hitted blocks by the sum of each modality so we will have a fair comparative plot
  #EXAMPLE OF WHAT I WILL GONNA TO DO
  #
  #                  | #0Gauss_MOD_A/(#0Gauss_MOD_A   +   #0Gauss_MOD_B)   ---  #0Gauss_MOD_B/(#0Gauss_MOD_A   +   #0Gauss_MOD_B)
  #                  | #1Gauss_MOD_A/(#1Gauss_MOD_A   +   #1Gauss_MOD_B)   ---  #1Gauss_MOD_B/(#1Gauss_MOD_A   +   #1Gauss_MOD_B)
  #                  | #2Gauss_MOD_A/(#2Gauss_MOD_A   +   #2Gauss_MOD_B)   ---  #2Gauss_MOD_B/(#2Gauss_MOD_A   +   #2Gauss_MOD_B)
  #                  | #3Gauss_MOD_A/(#3Gauss_MOD_A   +   #3Gauss_MOD_B)   ---  #3Gauss_MOD_B/(#3Gauss_MOD_A   +   #3Gauss_MOD_B)
  # hitted_blocks =  | .
  #                  | .
  #                  | ,
  #                  | #NGauss_MOD_A/(#NGauss_MOD_A   +   #NGauss_MOD_B)   ---  #NGauss_MOD_B/(#NGauss_MOD_A   +   #NGauss_MOD_B)

  
  for c in range(ubm_components):
  #for c in range(1):

    #norm_factor = sum(hitted_blocks_per_modality[0][c]) + sum(hitted_blocks_per_modality[1][c])
    minimum = min(min(hitted_blocks_per_modality[0][c]),min(hitted_blocks_per_modality[1][c]))
    maximum = max(max(hitted_blocks_per_modality[0][c]),max(hitted_blocks_per_modality[1][c]))
    norm_factor = maximum - minimum
    
    hitted_blocks_per_modality[0][c] = (hitted_blocks_per_modality[0][c] - minimum) / norm_factor
    hitted_blocks_per_modality[1][c] = (hitted_blocks_per_modality[1][c] - minimum)/ norm_factor

    #treating the nans
    NaNs = numpy.isnan(hitted_blocks_per_modality[0][c])
    hitted_blocks_per_modality[0][c][NaNs] = 0
      
    NaNs = numpy.isnan(hitted_blocks_per_modality[1][c])
    hitted_blocks_per_modality[1][c][NaNs] = 0
    

    #Saving modality A    
    block_img = block_image(img, args.block_size, args.block_overlap, hitted_blocks_per_modality[0][c]) #computing the block image
    output_file = os.path.join(args.output,args.modalities[0],"gaussian_{0}.jpg".format(c))
    bob.io.base.save(block_img.astype('uint8'),output_file)
    
    #Saving modality B
    block_img = block_image(img, args.block_size, args.block_overlap, hitted_blocks_per_modality[1][c]) #computing the block image 
    output_file = os.path.join(args.output,args.modalities[1],"gaussian_{0}.jpg".format(c))
    bob.io.base.save(block_img.astype('uint8'),output_file)

    
  sys.stdout.write('\n"Done!!!"'); sys.stdout.flush();
 

if __name__ == '__main__':
  main()
