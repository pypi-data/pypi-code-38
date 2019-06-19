#!/usr/bin/env python
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Sun Jan  15 19:12:43 CET 2017
#

"""
Tests GSVD

 Basically these tests test the GSVD relation.
 Given 2 matrices A and B  GSVD(A,B) = [U,V,X,C,S] where,

  A= (X * C.T * U^T)^T and 
  B= (X * S.T * V^T)^T and
  
  C**2 + S**2 = 1

"""

import bob.math
import numpy
import nose.tools
numpy.random.seed(10)


def gsvd_relations(A,B):
  [U,V,X,C,S] = bob.math.gsvd(A, B)

  # Cheking the relation  C**2 + S**2 = 1
  I = numpy.eye(A.shape[1])
  I_check = numpy.dot(C.T, C) + numpy.dot(S.T, S)
  nose.tools.eq_( (abs(I-I_check) < 1e-10).all(), True )

  # Cheking the relation A= (X * C.T * U^T)^T
  A_check = numpy.dot(numpy.dot(X,C.T),U.T).T
  nose.tools.eq_( (abs(A-A_check) < 1e-10).all(), True )

  # Cheking the relation B= (X * S.T * V^T)^T 
  B_check = numpy.dot(numpy.dot(X,S.T),V.T).T
  nose.tools.eq_( (abs(B-B_check) < 1e-10).all(), True )


def svd_relations(A):

  [U, S, V] = bob.math.svd(A)  
  A_check = numpy.dot(numpy.dot(V,S), U)
  nose.tools.eq_( (abs(A-A_check) < 1e-10).all(), True )


def test_first_case():
  
  #Testing the first scenario of gsvd:
  #M-K-L >= 0 (check http://www.netlib.org/lapack/explore-html/d1/d7e/group__double_g_esing_ga4a187519e5c71da3b3f67c85e9baf0f2.html#ga4a187519e5c71da3b3f67c85e9baf0f2)  

  A = numpy.random.rand(10,10)
  B = numpy.random.rand(790,10)

  gsvd_relations(A, B)


def test_second_case():
  
  #Testing the second scenario of gsvd:
  #M-K-L < 0 (check http://www.netlib.org/lapack/explore-html/d1/d7e/group__double_g_esing_ga4a187519e5c71da3b3f67c85e9baf0f2.html#ga4a187519e5c71da3b3f67c85e9baf0f2)  


  A = numpy.random.rand(4,5)
  B = numpy.random.rand(11,5)

  gsvd_relations(A, B)


def test_corner_case():

  #Testing when P <= N.


  A = numpy.random.rand(25, 25)
  B = numpy.random.rand(25, 25)
  gsvd_relations(A, B)



def test_svd_relation():

  ##Testing SVD

  A = numpy.random.rand(25, 25)
  svd_relations(A)

  #A = numpy.random.rand(20, 25)
  #svd_relations(A)

  A = numpy.random.rand(30, 25)
  svd_relations(A)



def test_svd_signal():

  ##Testing SVD signal
  ##This test was imported from bob.learn.linear  

  A = numpy.array([[3,-3,100], [4,-4,50], [3.5,-3.5,-50], [3.8,-3.7,-100]], dtype='float64')

  U_ref = numpy.array([[  2.20825004e-03,  -1.80819459e-03,  -9.99995927e-01],
                       [ -7.09549949e-01,  7.04649416e-01,  -2.84101853e-03],
                       [ 7.04651683e-01,  7.09553332e-01,  2.73037723e-04]])
  
  [U,S,V] = bob.math.svd(A)
  nose.tools.eq_((abs(U-U_ref) < 1e-8).all(), True)
  svd_relations(A)
  

  
def test_svd_signal_book_example():

  ## Reference copied from here http://prod.sandia.gov/techlib/access-control.cgi/2007/076422.pdf  

  A = numpy.array([[2.5, 63.5, 40.1, 78, 61.1],
                   [0.9, 58.0, 25.1, 78, 94.1],
                   [1.7, 46.0, 65.0, 78, 106.4],
                   [1.2, 15.7, 102.1, 78, 173.0],
                   [1.5, 12.2, 100.0, 77, 199.7],
                   [2.0, 8.9, 87.8, 76, 176.0],
                   [3.8, 2.7, 17.1, 69, 373.6],
                   [1.0, 1.7, 140.0, 73, 283.7],
                   [2.1, 1.0, 55.0, 79, 34.7],
                   [0.8, 0.2, 50.4, 73, 36.4]])

  [U,S,V] = bob.math.svd(A)
  assert U[0,0] > 0
  svd_relations(A)
  
  

