from __future__ import division 
from __future__ import absolute_import
from __future__ import print_function

import pandas as pd 
import numpy as np
import collections

from . import config 


class ConfusionMatrix:
  '''
  Confusion matrix utility class that wraps a pandas
  dataframe and provides misc metric utility properties
  '''

  def __init__( self, cmat ):
    if len( cmat ) != len( cmat.columns ):
      raise ValueError( 'ConfusionMatrix must be a square matrix' )
    if not ( cmat.index == cmat.columns ).all():
      raise ValueError( 'ConfusionMatrix rows must be identical to its columns' )
    self.cmat = cmat 

  @property
  def classes( self ):
    ''' List of classes used '''
    return self.cmat.columns 

  @property
  def num_classes( self ):
    ''' Total number of classes '''
    return len( self.classes )
  
  @property
  def support( self ):
    ''' tp+fn for each class '''
    return self.cmat.sum( axis=1 )

  @property
  def frac_support( self ):
    ''' Fraction of total number of points for each class '''
    return self.support / self.total 
  

  @property
  def total( self ):
    ''' tp+fp+fn+tn in the entire cmat '''
    return self.support.sum()

  @property
  def accuracy( self ):
    ''' Overal accuracy '''
    return np.diag( self.cmat ).sum() / self.total 
  
  @property
  def recall( self ):
    ''' tp / (tp+fn) for each class '''
    return ( np.diag( self.cmat ) / self.cmat.sum( axis=1 ))

  @property
  def average_recall( self ):
    ''' Average class recall '''
    return self.recall.mean()

  @property
  def precision( self ):
    ''' Returns tp / (tp+fp) for each class '''
    return ( np.diag(self.cmat) / self.cmat.sum( axis=0 ))

  @property
  def average_precision( self ):
    ''' Average class precision '''
    return self.precision.mean()

  @property
  def f1score( self ):
    ''' 2*tp / (2*tp+fp+fn) for each class '''
    return (2*np.diag(self.cmat) / (self.cmat.sum( axis=0 )+self.cmat.sum( axis=1 )))

  @property
  def average_f1score( self ):
    ''' Average class f1 score '''
    return self.f1score.mean()

  @property
  def iou( self ):
    ''' tp / (2*tp+fp+fn) for each class '''
    return (np.diag(self.cmat) / (self.cmat.sum( axis=0 )+self.cmat.sum( axis=1 )-np.diag(self.cmat)))

  @property
  def average_iou( self ):
    ''' Average class iou '''
    return self.iou.mean()

  @property
  def class_report(self):
    return pd.DataFrame( dict(
      precision=self.precision,
      recall=self.recall,
      f1score=self.f1score,
      iou=self.iou,
      frac_support=self.frac_support,
      support=self.support,
    ))[['precision', 'recall', 'f1score', 'iou', 'frac_support', 'support',]]
  
  @property
  def report( self ):
    return pd.Series( dict(
      accuracy=self.accuracy,
      precision=self.average_precision,
      recall=self.average_recall,
      f1score=self.average_f1score,
      iou=self.average_iou
    ))[['accuracy','precision','recall','f1score','iou']]
  

  def __str__( self ):
    return self.cmat.__repr__()

  def __repr__( self ):
    return '<ConfusionMatrix: num_classes=%s>'%self.num_classes

  def __getitem__( self, k ):
    if not type( k ) in {list,tuple}:
      raise ValueError( 'Subscript type must be a list or tuple' )
    return ConfusionMatrix( self.cmat[k].loc[k] )

  @staticmethod
  def create( y_true, y_pred, labels=None, names=None ):
    '''
    Create a confusion matrix as a pandas dataframe where
    the rows (first axis) are the true values and the
    columns (second axis) are the predicted values
    '''
    # Convert to numpy array
    y_true, y_pred = np.asarray( y_true ), np.asarray( y_pred )
    # Make sure they are rank1 
    if not len( y_true.shape ) == 1:
      raise ValueError( 'y_true must be a rank 1 tensor. Received shape: %s'%y_true.shape )
    if not len( y_pred.shape ) == 1:
      raise ValueError( 'y_pred must be a rank 1 tensor. Received shape: %s'%y_pred.shape )
    # Dynamically compute labels if not provided
    labels = labels or sorted( set( y_true ) | set( y_pred ))
    # Default to use label values for names
    names = names or labels or list( set( y_true ) | set( y_pred ))
    # Wrap y_true, y_pred in pandas series
    y_true, y_pred = pd.Series( y_true ), pd.Series( y_pred )
    # Make sure lengths match up
    if not len( y_true ) == len( y_pred ):
      raise ValueError( 'y_true and y_pred must have the same length: %s vs %s'%(len(y_true),len(y_pred)) )
    if not len( labels ) == len( names ):
      raise ValueError( 'labels and names must have the same length: %s vs %s'%(len(labels),len(names)) )
    # Make sure all values are valid 
    if not y_true.isin( labels ).all():
      raise ValueError( 'Not all y_true values are among valid labels' )
    if not y_pred.isin( labels ).all():
      raise ValueError( 'Not all y_pred values are among valid labels' )
    # Create a dict for mapping label value -> label index
    label_map = dict( map( reversed, enumerate( labels )))
    y_true, y_pred = y_true.replace( label_map ), y_pred.replace( label_map )
    # Count occurences of (y_true,y_pred) tuples
    indices, count = zip( *collections.Counter( zip( y_true, y_pred )).items() )
    # Separate list of true/pred indices 
    t,p  = zip( *indices )
    # Initialize confusion matrix
    cmat = np.zeros((len(labels),len(labels)), dtype=int )
    # Set count entries
    cmat[t,p] = count 
    # Wrap in pandas dataframes with name index 
    cmat = pd.DataFrame( cmat, index=names, columns=names )
    return ConfusionMatrix( cmat )


  @staticmethod
  def load( filepath ):
    '''
    Load a confusion matrix from json
    '''
    return ConfusionMatrix( pd.read_csv( filepath, index_col=0 ))


  def save( self, filepath ):
    '''
    Save the current cmat to csv
    '''
    self.cmat.to_csv( filepath )


  VALID_CMAT_FILTERS = {'true', 'pred', 'either', 'both' }
  def drop_zero( self, mode ):
    '''
    Filter zero rows and/or columns in a cmat
    '''
    nonzero_rows = self.cmat.sum( axis=1 ) > 0
    nonzero_cols = self.cmat.sum( axis=0 ) > 0

    if mode == 'pred':
      # Filter classes where no predictions (columns is zero)
      filt = nonzero_cols 
    elif mode == 'true':
      filt = nonzero_rows 
    elif mode == 'either':
      # Either axis is zero -> not both axes are nonzero
      filt = nonzero_cols & nonzero_rows
    elif mode == 'both':
      # Both axes are zero -> not either axis is nonzero
      filt = nonzero_cols | nonzero_rows  
    else:
        raise ValueError( 'Invalid "mode" argument (%s) must be one of: %s'%(mode, ConfusionMatrix.VALID_CMAT_FILTERS) )
    classes = self.cmat.index[filt]
    filtered_cmat = self.cmat[classes].loc[classes]
    return ConfusionMatrix( filtered_cmat )


  VALID_CMAT_NORMALIZATION = {'recall', 'precision', 'f1score', 'iou'}
  def normalize( self, mode ):
    '''
    Normalize a confusion matrix, with respect to precision,
    recall, f1score, or iou (intersection over union).
    '''
    col_sums = self.cmat.sum( axis=0 )
    row_sums = self.cmat.sum( axis=1 )
    if mode == 'recall':
      # Divide by row sums 
      normed_cmat = self.cmat.div( row_sums, axis=0 ).fillna( 0. ) # Recall
    elif mode == 'precision':
      # Divide by column sums 
      normed_cmat = self.cmat.div( col_sums, axis=1 ).fillna( 0. ) # Precision
    elif mode == 'f1score':
      # Normalize so that the diagonal is the f1scores
      union_plus_tp = np.array( np.meshgrid( col_sums, row_sums ))\
                        .transpose( 1,2,0 ).sum( axis=2 )
      normed_cmat = (2*self.cmat).div( union_plus_tp )
    elif mode == 'iou':
      # Normalize so that the diagonal is the ious
      # Compute intersection/union for every possible combination in the cmat
      union = np.array( np.meshgrid( col_sums, row_sums ))\
                .transpose( 1,2,0 ).sum( axis=2 ) - self.cmat
      normed_cmat = self.cmat.div( union ).fillna( 0. )
    else:
      raise ValueError( 'Invalid "mode" argument (%s) must be one of: %s'%(mode, ConfusionMatrix.VALID_CMAT_NORMALIZATION) )

    return ConfusionMatrix( normed_cmat )


  def plot( self, ax=None, title=None, plot_text=None ):
    '''
    Plot a confusiono matrix 
    '''
    plt = config.pyplot() #  matplotlib.pyplot
    if ax is None:
      size = max( self.num_classes, 5 )
      plt.figure( figsize=(size,size) )
      ax = plt.gca()
        
    fig  = ax.get_figure()
    fig.patch.set_facecolor( config.fig_facecolor )
    for spine in ax.spines.values():
      spine.set_visible(False)
    heatmap = ax.pcolor( self.cmat[::-1], cmap=config.heatmap_cmap, edgecolor=config.heatmap_edge_color, linewidth=1 )
    
    H, W = fig.get_size_inches()*fig.dpi
    M, N = self.cmat.shape
    dpr  = min( H/M, W/N, 50 )
    plot_text = dpr > 20 if plot_text is None else plot_text
    floating  = not any( 'int' in str(dtype) for dtype in self.cmat.dtypes )
    if plot_text:
      for (i,j),v in np.ndenumerate( self.cmat.values ):
        text = '.%.0f'%(v*100) if floating else str(v)
        ax.text(j+0.5, M-i-0.5, text, fontsize=12*dpr/40, 
                va='center', ha='center', color=config.heatmap_font_color, alpha=0.7 )
    
    ax.set_title( title or 'Confusion Matrix' )
    ax.set_yticks( np.arange( 0.5, len(self.cmat.index), 1) )
    ax.set_yticklabels( self.cmat.index[::-1], minor=False )
    ax.set_ylabel( 'Ground Truth' )
    ax.xaxis.set_label_position( 'top' )
    ax.xaxis.tick_top()
    ax.set_xlabel( 'Predicted' )
    ax.set_xticks( np.arange(0.5, len(self.cmat.columns), 1) )
    ax.set_xticklabels( self.cmat.columns, minor=False, rotation=90 )
    ax.set_aspect( 'equal' )
    plt.colorbar( heatmap, ax=ax )
    plt.tight_layout()

    return ax 
