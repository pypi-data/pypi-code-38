#!python

# ############################### #
# trainWoolf.py
#
# Script to build a woolf model.
#
# Anna Farrell-Sherman 11/5/18
# ############################### #

from argparse import ArgumentParser, ArgumentTypeError #used to create command line inputs
import sys # for error handeling

#import Woolf module for classifier building
import trainWoolf

##################################################################################
#Default Values
# If you know enough python to alter the script, you can change the default values
# here instead of on the command line.
##################################################################################
scalingType = 'MinMaxScaler' # EX: 'StandardScaler'
scoringMetric = 'MCC' #EX: ‘f1’
crossFolds = 5 #EX: 10
nNeighbors = range(1,20)
nTrees = range(1,15,2)
minLeafSize = range(10,30,3)

#The parameter grid can take the place of the algorithm inputs above, and allows
# adjustment of more parameters in the classifier algorithm
pGrid = None
#EX: {'clf__n_estimators': range(1,20), 'clf__min_samples_leaf': range(3,30,3)}
##################################################################################
##################################################################################

parser = ArgumentParser(description="Create a Woolf Model based a feature table")
parser.add_argument("featureTable", help="A CSV file containing feature data from a set of sequences")

#choose machine learning algorithm
group = parser.add_mutually_exclusive_group()
group.add_argument("-k", "--kNN", action="store_true")
group.add_argument("-f", "--randomForest", action="store_true")

#kNN arguments
parser.add_argument("-n", "--nNeighbors", type=parseRange, help="number of neighboors for kNN classifier.  Ranges are expresed as low-hi,jump (1-7,2 would test 1,3,5 and 7")

#random Forest arguments
parser.add_argument("-t", "--nTrees", type=parseRange, help="number of trees for random forest classifier.  Ranges are expresed as low-hi,jump (1-7,2 would test 1,3,5 and 7")
parser.add_argument("-l", "--minLeafSize", type=parseRange, help="minimum size of leaves in each tree of the random forest classifier.  Ranges are expresed as low-hi,jump (1-7,2 would test 1,3,5 and 7")

#set up learning parameters
parser.add_argument("-s", "--featureScaler", help="A scikit learn scaler object to scale in the input features")
parser.add_argument("-c", "--crossValidationFolds", help="The number of cross validation folds to execute")
parser.add_argument("-a", "--accuracyMetric", help="A scikit learn accuracy metric for training")

#add functionality
parser.add_argument("-p", "--predictFeatureTable", help="A unclassified feature table to be predicted by the model")
parser.add_argument("-e", "--listErrors", action="store_true", help="Include to see a list of which sequences in the training dataset were missclassified")


#add verbose argument
parser.add_argument("-v", "--verbose", action="store_true", help="Inlcude to get more detailed output")

args = parser.parse_args()

##################################################################################

#Check that arugments were provided
if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)

#update learning parameters if needed
scalingType = args.featureScaler if args.featureScaler else scalingType
scoringMetric = args.accuracyMetric if args.accuracyMetric else scoringMetric
crossFolds = args.crossValidationFolds if args.crossValidationFolds else crossFolds
nNeighbors = args.nNeighbors if args.nNeighbors else nNeighbors
nTrees = args.nTrees if args.nTrees else nTrees
minLeafSize = args.minLeafSize if args.minLeafSize else minLeafSize

#Determine which classifier type was selected
if args.kNN:
	classifierType = 'kNN'
	print('Building kNN Woolf Model...')
elif args.randomForest:
	classifierType = 'fOREST'
	print('Building Random Forest Woolf Model...')
else:
	print('ERROR: Please choose either kNN (-k) or Random Forest (-f)')
	exit()

if args.verbose:
	print("Cross-validation Folds: " + str(crossFolds))
	print("Scoring Metric: " + str(scoringMetric))
	print("Scaler type: " + str(scalingType))

try:
	#Build the model
	woolf = buildWoolf(classifierType, pGrid, scalingType, int(crossFolds), scoringMetric, nNeighbors, nTrees, minLeafSize)

	#Train the model
	print("Training Model...")
	results = trainModel(woolf, args.featureTable)
except (ValueError, TypeError) as e:
	print("Invalid Input: " + str(e))
	exit()


#OUTPUT
print("~~~~~~    RESULTS    ~~~~~~")
print("Score of best classifier: " + str(results.best_score_))
#print("Standard deviation of best score: " + str(results.cv_results_['std_test_score'][results.best_index_]))
print("Best Params:" + str(results.best_params_))
if args.verbose:
	print("Range of classifier scores across hyperparameters:")
	print("\tMax: " + str(results.best_score_))
	print("\tMin: " + str(min(results.cv_results_['mean_test_score'])))
	#print("\tParams: " + str(results.cv_results_['params']))
	#print("\tValues: " + str(results.cv_results_['mean_test_score']))
	#print("\tSD: " + str(results.cv_results_['std_test_score']))
	print("Range of training scores across hyperparameters:")
	print("\tMax: " + str(max(results.cv_results_['mean_train_score'])))
	print("\tMin: " + str(min(results.cv_results_['mean_train_score'])))
print("~~~~~~               ~~~~~~")

#Print misclassified sequences
if args.listErrors:
	print("Listing misclassified instances")
	posErrors, negErrors = findMisclassified(woolf, args.featureTable)
	print("misclassified as positive class:\n " + str(posErrors))
	print("misclassified as negative class:\n " + str(negErrors))

#Predict new instances
if args.predictFeatureTable:
	print("Predicting novel instances")
	try:
		prediction, score = predictWoolf(woolf, args.predictFeatureTable)
		print(prediction)
		if score:
			print("Score on test data: " + str(score))
	except FileNotFoundError:
		print("ERROR: Feature Table not found: " + args.predictFeatureTable)
