""" Init file for SRPPolarimetry

Context : SRP
Module  : Polarimetry
Version : 1.6.0
Author  : Stefano Covino
Date    : 20/08/2018
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino

Usage   : to be imported

History : (21/02/2012) First named version.
        : (29/02/2012) Wave plate matrix added.
        : (02/09/2013) ISM matrix added.
        : (16/07/2014) PolBias added.
        : (20/01/2015) Simple transmission matrix added.
        : (22/05/2015) Polarizer matrix added.
        : (17/02/2017) Rayleigh sky model.
        : (30/03/2017) Alternative formulation of the metallic mirror matrix.
        : (09/05/2017) Better formulation of Mueller transmission matrix in case of beam splitting.
        : (18/09/2017) Cnt2Stoke.
        : (20/08/2018) Polarization limits based on Plaszczynski et al. (2014).
"""


__all__ = ['AluminiumRefractiveIndex','Cnt2Stoke', 'MuellerISMMatrix','MuellerMetallicMirrorMatrix',
           'MuellerMetallicMirrorMatrixAlter','MuellerRotationMatrix','MuellerTransmissionMatri',
           'MuellerHalfWavePlateMatrix','MuellerPolarizerMatrix', 'MuellerQuarterWavePlateMatrix',
           'MuellerThomsonRayleighScatteringMatrix','MuellerWavePlateMatrix','Pol2Stokes',
           'PolBias','PolBiasLims', 'RayleighSkyModel','Stokes2Pol','TransmissionMatrix']



