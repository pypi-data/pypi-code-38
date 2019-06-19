#!/usr/bin/env python3

# ############################### #
# trainWoolf.py
#
# Script to build a woolf model.
#
# Anna Farrell-Sherman 11/5/18
# ############################### #

#used to create command line inputs
from argparse import ArgumentParser, ArgumentTypeError

#import needed machine learning packages
from sklearn import neighbors #for the kNN
from sklearn.ensemble import RandomForestClassifier #for the randomforest
from sklearn.metrics import matthews_corrcoef, make_scorer

from sklearn.model_selection import GridSearchCV # for parameter estimation
from sklearn.pipeline import Pipeline #to allow for normalization in cross validation
from sklearn.preprocessing import MinMaxScaler, StandardScaler, MaxAbsScaler, RobustScaler #minMax normalization

#other functionality
import pandas as pd #to import the csv datafile
import numpy as np # to read in length as float64
from ast import literal_eval #to decode dictionaries entered for parameter grids
import sys # for error handeling


def buildWoolf(classifierType, pGrid, scalerString, cvFolds, scoringM, nNhrs, nTrs, minL):
	'''Creates the Woolf Model with all user given parameters '''

    #Classifiers and Param Grids
	if classifierType == 'kNN':
		clf = neighbors.KNeighborsClassifier(weights='uniform')
		param_grid = {'clf__n_neighbors': nNhrs} if pGrid == None else pGrid
	elif classifierType == 'fOREST':
		clf = RandomForestClassifier(random_state=42)
		param_grid = {'clf__n_estimators': nTrs, 'clf__min_samples_leaf': minL} if pGrid == None else pGrid
	else:
		raise NameError("Unrecognized classifier type: " + classifierType)

	scaler = scaler_selector(scalerString)
	accM = accM_selector(scoringM)

    #create pipe to allow for scaling in cross-validation
	pipe = Pipeline([('scaler', scaler), ('clf', clf)])

    #create grid for hyperparameter searching
	gridModel = GridSearchCV(pipe, param_grid, cv=cvFolds, scoring=accM, return_train_score=True, iid=False)

	return gridModel



def trainModel(woolfModel, inputCSV):
	'''Train a woolf model with a binary class feature table'''

    #Set Up data
	sequenceFeatureTable = pd.read_csv(inputCSV, header = 0, dtype={'Length':  np.float64})
	seqTarget = sequenceFeatureTable['Class']
	seqIDs = sequenceFeatureTable['ID']
	seqData = sequenceFeatureTable.drop(columns=['Class', 'ID'])

    #fit model to data on provided parameter grid
	woolfModel.fit(seqData, seqTarget)

	return woolfModel

def findMisclassified(woolfModel, inputCSV):
	'''Find all the missclassified items in a binary class feature table'''

    #Set Up data
	sequenceFeatureTable = pd.read_csv(inputCSV, header = 0, dtype={'Length':  np.float64})
	seqTarget = sequenceFeatureTable['Class']
	seqIDs = sequenceFeatureTable['ID']
	seqData = sequenceFeatureTable.drop(columns=['Class', 'ID'])

    #Grid model to data
	predictions = woolfModel.predict(seqData)

	misAsPos = []
	misAsNeg = []
	for i in range(len(seqIDs)):
		if seqTarget[i] == 0 and predictions[i] == 1:
			misAsPos.append(seqIDs[i])
		elif seqTarget[i] == 1 and predictions[i] == 0:
			misAsNeg.append(seqIDs[i])

	return misAsPos, misAsNeg


def predictWoolf(woolfModel, predictCSV):
	'''Predict the class of new feature sets with a created woolf model'''

	#Set Up data
	sequenceFeatureTable = pd.read_csv(predictCSV, header = 0, dtype={'Length':  np.float64})
	seqIDs = sequenceFeatureTable['ID']
	seqData = sequenceFeatureTable.drop(columns=['ID'])

	#determine if class labels are in dataframe
	classLabled = True if 'Class' in list(sequenceFeatureTable) else False
	score = None

	#if there are class labels in dataframe
	if classLabled:
		correctClass = sequenceFeatureTable['Class']
		seqData = seqData.drop(columns=['Class'])
		score = woolfModel.score(seqData, correctClass)

	#print(list(sequenceFeatureTable))

    #predict classes
	predictions = woolfModel.predict(seqData)

	#Attach IDs to predictions
	resultsDict = dict(zip(seqIDs, predictions))

	return resultsDict, score


def parseRange(rangeString):
	'''Looks at inputed range from command line and parses it into a python object'''
	try:
		if ',' in rangeString:
			lo, hi = rangeString.split('-')
			hi, jump = hi.split(',')
			res = list(range(int(lo), int(hi)+1, int(jump)))
		elif '-' in rangeString:
			lo, hi = rangeString.split('-')
			res = list(range(int(lo), int(hi)+1))
		elif rangeString.isdigit():
			res = [int(rangeString)]
	except:
		raise ArgumentTypeError("'" + rangeString + "' is not a valid range of numbers. Expected formats: '1' '1-10' or '1-10,2'.")
	return res

def scaler_selector(inputString):
	'''determine which scaling type was selected'''
	scalers = {'MinMaxScaler': MinMaxScaler(), 'StandardScaler': StandardScaler(),
		'MaxAbsScaler': MaxAbsScaler(), 'RobustScaler': RobustScaler(), 'None': None}
	scaler = scalers.get(inputString , '')
	if scaler == '': #raise error if not found
		raise TypeError(inputString)
	return scaler

def accM_selector(inputString):
	'''#determine which accuracy metric type was selected'''
	accMs = {'MCC': make_scorer(matthews_corrcoef), 'f1': 'f1',
		'accuracy': 'accuracy', 'precision': 'precision', 'recall': 'recall'}
	accM = accMs.get(inputString , '')
	if accM == '': #raise error if not found
		raise TypeError(inputString)
	return accM