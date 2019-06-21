#!/usr/bin/env python
# encoding: utf-8

def load_timestamps(filename):
  """ load timestamps of a recording.
  
  Each line of the file contains two numbers: 
  the frame index and the corresponding time in milliseconds.
  
  Parameters
  ----------
  filename: str
    The file to extract timestamps from.

  Returns
  -------
  dict:
    Dictionary with frame index as key and timestamp as value.
  """
  timestamps = {}
  f = open(filename, 'r')
  for line in f:
    line = line.rstrip('\n')
    splitted = line.split(' ')
    timestamps[int(splitted[0])] = int(splitted[1])   
  f.close()
  return timestamps

