# import sys, os 
# sys.path.append( os.path.join( os.path.dirname( __file__ ), '..' ) )
import numpy as np 
import pandas as pd 

from . import ConfusionMatrix

y_true = [1,1,3,1]
y_pred = [1,2,2,1]
labels = [1,2,3]
names  = ['foo','bar','baz']

def test_create_cmat():
  ''' 
  Check that constructing method, called with ideal arguments,
  does not throw a weird error
  '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )

def test_create_cmat_names_ok():
  ''' Check that names are correctly set, either explicityly or dynamically '''
  # Create with explicit names
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert np.all( cm.cmat.columns == np.array(names) )
  assert np.all( cm.cmat.index == np.array(names) )
  # Create without explicit names, labels should be used
  cm = ConfusionMatrix.create( y_true, y_pred, labels )
  assert np.all( cm.cmat.columns == np.array(labels) )
  assert np.all( cm.cmat.index == np.array(labels) )

def test_create_cmat_labels_ok():
  ''' Check that labels are correctly set or dynamically created '''
  # Create with explicit labels 
  cm = ConfusionMatrix.create( y_true, y_pred, labels+[4] )
  assert cm.cmat.shape == (4,4)
  # Create with dynamically discovered labels 
  cm = ConfusionMatrix.create( y_true, y_pred  )
  assert cm.cmat.shape == (3,3)
  assert np.all( cm.cmat.columns == np.array( labels ))
  assert np.all( cm.cmat.index == np.array( labels ))

def test_classes():
  ''' Check that classes returns the provided labels '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert cm.num_classes == 3
  assert np.all( cm.classes == np.array( names ))

def test_support():
  ''' Check that support correctly returns support for each class '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  expected = pd.Series([3,0,1], index=names )
  assert np.all( expected.index == cm.support.index )
  assert np.all( expected == cm.support )
  # Check fractional support 
  expected = pd.Series([0.75, 0, 0.25], index=names )
  assert np.all( expected.index == cm.frac_support.index )
  assert np.all( expected == cm.frac_support )

def test_total():
  ''' Check that total entries works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert cm.total == len(y_true)


def test_matrix():
  ''' 
  Check that the acutal matrix computed is correct 
  The expected array was computed over y_true/y_pred
  with sklearn.metrics.confusion_matrix
  '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  expected = np.array([
    [2, 1, 0],
    [0, 0, 0],
    [0, 1, 0]
  ])
  assert np.all( cm.cmat == expected )

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Test classification analysis
# The following expected numbeers were computed
# with sklearn.metric.classification_report where
# appropriate
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def test_accuracy():
  ''' Check that overal accuracy works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert cm.accuracy == 0.5

def test_recall():
  ''' Check that per-class recall works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  recall = cm.recall 
  assert recall['foo'] == 2/3
  assert recall['baz'] == 0
  # Bar recall should be nan because it does not occurr in y_true 
  # This behavior differs from sklearn, which would set it to zero
  assert recall.isna()['bar']

def test_average_recall():
  ''' Test that class average recall works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  # Average recall should ignore "bar" since it is nan
  # and, therefore, only divide by 2. This is also different
  # from sklearn which would just set recall for "bar" to zero
  assert cm.average_recall == (2/3 + 0)/2

def test_precision():
  ''' Test that per-class precision works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  precision = cm.precision 
  assert precision['foo'] == 1
  assert precision['bar'] == 0
  # Same as with recall, precision should be nan for "baz" since there is
  # no mention of it in y_pred
  assert precision.isna()['baz']

def test_average_precision():
  ''' Test that class average precision works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  # Again, since there is no mention of "baz" in y_pred,
  # its precision should be nan, so we divide by 2
  assert cm.average_precision == (1+0)/2

def test_f1score():
  ''' Test that per-class f1score works as intended '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  expected = pd.Series( [0.8,0,0], index=names )
  assert np.all( cm.f1score == expected )

def test_average_f1score():
  ''' Test that class average f1 score works as intended '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert cm.average_f1score == (0.8+0+0)/3

def test_iou():
  '''
  Test that per-class iou works. This metric is not a part of the sklearn
  classification report (though notably proportional-ish to f1score).
  For classification it is simply the number of datapoints where
  both the prediction and ground truth agrees on a class (true positive), over
  the number of datapoints where either the prediction or ground truth 
  contains the class (true positive + false positives + false negatives)
  '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  expected = pd.Series( [2/3, 0, 0], index=names )
  assert np.all( expected == cm.iou )

def test_averrage_iou():
  ''' Test that class average iou works '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  assert cm.average_iou == (2/3 + 0 + 0)/3



def test_class_report():
  ''' 
  Test that the per-class report works as intended 
  Since the individual metrics have been tested above, it
  should be sufficient to test that the right values go
  to the right place
  '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  rep = cm.class_report.fillna(-99)
  assert rep.shape == (3,6)
  assert np.all( rep['precision'] == cm.precision.fillna(-99) )
  assert np.all( rep['recall'] == cm.recall.fillna(-99) )
  assert np.all( rep['f1score'] == cm.f1score )
  assert np.all( rep['iou'] == cm.iou )
  assert np.all( rep['support'] == cm.support )
  assert np.all( rep['frac_support'] == cm.frac_support )


def test_report():
  ''' Test the class average report '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  rep = cm.report 
  assert rep.shape == (5,)
  assert rep['accuracy'] == cm.accuracy
  assert rep['precision'] == cm.average_precision
  assert rep['recall'] == cm.average_recall
  assert rep['f1score'] == cm.average_f1score
  assert rep['iou'] == cm.average_iou



# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Test normalization 
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def test_normalize_recall():
  ''' 
  Test that normalization by recall works - rows should sum up to one 
  Note that the diagonal of this matrix should be equal to 
  cm.recall where it is not NaN
  '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_normed = cm.normalize( 'recall' )
  diag = pd.Series( np.diag( cm_normed.cmat ), index=names )
  # Diagonal should be equal to recall
  assert np.all( cm.recall.fillna(0) == diag )
  row_sum = cm_normed.cmat.sum( axis=1 )
  # Non-na recall should make the row sum up to 1
  assert row_sum['foo'] == 1
  assert row_sum['bar'] == 0 # Recall is nan
  assert row_sum['baz'] == 1

def test_normalize_precision():
  ''' Test normalization wrt. precision '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_normed = cm.normalize( 'precision' )
  diag = pd.Series( np.diag( cm_normed.cmat ), index=names )
  # Diagonal should be equal to precision
  assert np.all( cm.precision.fillna(0) == diag )
  col_sum = cm_normed.cmat.sum( axis=0 )
  # Non-na precision should make the row sum to 1
  assert col_sum['foo'] == 1
  assert col_sum['bar'] == 1
  assert col_sum['baz'] == 0

def test_normalize_f1score():
  ''' Test normalization wrt. f1score ''' 
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_normed = cm.normalize( 'f1score' )
  diag = pd.Series( np.diag( cm_normed.cmat ), index=names )
  assert np.all( diag == cm.f1score )


def test_normalize_iou():
  ''' Test normalization wrt. iou ''' 
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_normed = cm.normalize( 'iou' )
  diag = pd.Series( np.diag( cm_normed.cmat ), index=names )
  assert np.all( diag == cm.iou )



# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Test filtering of zero rows/columns
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def test_drop_zero_true():
  ''' Test dropping classes where rows sums to zero (no y_true) '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_filtered = cm.drop_zero( 'true' )
  assert cm_filtered.cmat.shape == (2,2)
  # Bar has zero samples in y_pred, so it should be gone 
  assert np.all( cm_filtered.cmat.columns == np.array(['foo','baz']) )
  assert np.all( cm_filtered.cmat.index == np.array(['foo','baz']) )

def test_drop_zero_pred():
  ''' Test dropping classes where columns sums to zero (no y_pred) '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_filtered = cm.drop_zero( 'pred' )
  assert cm_filtered.cmat.shape == (2,2)
  # Bar has zero samples in y_pred, so it should be gone 
  assert np.all( cm_filtered.cmat.columns == np.array(['foo','bar']) )
  assert np.all( cm_filtered.cmat.index == np.array(['foo','bar']) )


def test_drop_zero_either():
  ''' Test dropping classes where columns or rows sums to zero (no y_pred or no y_true) '''
  cm = ConfusionMatrix.create( y_true, y_pred, labels, names )
  cm_filtered = cm.drop_zero( 'either' )
  assert cm_filtered.cmat.shape == (1,1)
  # Bar has zero samples in y_pred, so it should be gone 
  assert np.all( cm_filtered.cmat.columns == np.array(['foo']) )
  assert np.all( cm_filtered.cmat.index == np.array(['foo']) )


def test_drop_zero_both():
  ''' Test dropping classes where columns and rows sums to zero (no y_pred and no y_true) '''
  # Need to add one more class to facilitate expected behavior
  cm = ConfusionMatrix.create( y_true, y_pred, labels+[9], names+['asdf'] )
  assert cm.cmat.shape == (4,4)
  cm_filtered = cm.drop_zero( 'both' )
  assert cm_filtered.cmat.shape == (3,3)
  # Bar has zero samples in y_pred, so it should be gone 
  assert np.all( cm_filtered.cmat.columns == np.array(['foo','bar','baz']) )
  assert np.all( cm_filtered.cmat.index == np.array(['foo','bar','baz']) )