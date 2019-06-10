""" Init file for SRPMath

Context : SRP
Module  : Math
Version : 1.6.0
Author  : Stefano Covino
Date    : 14/03/2017
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (29/09/2010) First named version.
        : (08/11/2010) Cartesian distance added.
        : (09/02/2012) Sidereal time, hour and parallactic angles computation added.
        : (11/02/2012) PointMatch added.
        : (18/02/2012) Sky functions moved to SRPSky.
        : (23/08/2012) New angular distance function.
        : (20/09/2012) Angular phasing function.
        : (18/11/2014) Doppler factor function.
        : (10/11/2015) BiGauss function.
        : (18/11/2015) raw_moment function.
        : (27/11/2015) findPercArea function.
        : (28/01/2016) integFuct function.
        : (14/03/2017) AngleRange function.
"""


__all__ = ['AngleRange','AngularDistance', 'AstroAngleInput', 'AstroCoordInput', 'AstroMagInput',
           'BiGauss','CartesiamCoordAmpRotoTranslation','CartesianDistance', 'CartesianVectorClass',
           'DopplerFactor','FastAngularDistance', 'findPercArea','inetgFuct',
           'InverseCartesiamCoordAmpRotoTranslation','LorentzFactor','MinDist', 'PhaseAngle',
           'PointClass', 'PointMatch', 'raw_moment','TriangleClass']


