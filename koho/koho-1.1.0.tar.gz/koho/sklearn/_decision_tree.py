# encoding=utf-8
""" Decision Tree module.

- Classification
- Numerical (dense) data
- Missing values (Not Missing At Random (NMAR))
- Class balancing
- Multi-Class
- Multi-Output (single model)
- Build order: depth first
- Impurity criteria: gini
- Split a. features: best over k (incl. all) random features
- Split b. thresholds: 1 random or all thresholds
- Stop criteria: max depth, (pure, no improvement)
- Important Features
- Export Graph

Implementation Optimizations:
stack, samples LUT with in-place partitioning, incremental histogram updates

Python interface compatible with scikit-learn.
"""

# Author: AI Werkstatt (TM)
# (C) Copyright 2019, AI Werkstatt (TM) www.aiwerkstatt.com. All rights reserved.

# Scikit-learn compatible
# http://scikit-learn.org/stable/developers
# Trying to be consistent with scikit-learn's decision tree module
# https://github.com/scikit-learn/scikit-learn
# Basic concepts for the implementation of the classifier are based on
# G. Louppe, “Understanding Random Forests”, PhD Thesis, 2014

import numbers
import numpy as np
import scipy
import operator
from functools import reduce
from sklearn.base import BaseEstimator, ClassifierMixin, MultiOutputMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted, check_consistent_length
from sklearn.utils.multiclass import unique_labels

from io import StringIO

# Cython binding for C++ implementation
from ._decision_tree_cpp import RandomState, Tree, DepthFirstTreeBuilder

# ==============================================================================
# Decision Tree Classifier
# ==============================================================================


class DecisionTreeClassifier(BaseEstimator, ClassifierMixin, MultiOutputMixin):
    """ A decision tree classifier.,

    Parameters
    ----------
    class_balance : str 'balanced' or None, optional (default='balanced')
        Weighting of the classes.

            - If 'balanced', then the values of y are used to automatically adjust class weights
              inversely proportional to class frequencies in the input data.
            - If None, all classes are supposed to have weight one.

    max_depth : int or None, optional (default=None)
        The maximum depth of the tree.

            The depth of the tree is expanded until the specified maximum depth of the tree is reached
            or all leaves are pure or no further impurity improvement can be achieved.
            - If None, the maximum depth of the tree is set to max long (2^31-1).

    max_features : int, float, str or None, optional (default=None)
        Note: only to be used by Decision Forest

        The number of random features to consider when looking for the best split at each node.

            - If int, then consider ``max_features`` features.
            - If float, then ``max_features`` is a percentage and
              int(``max_features`` * n_features) features are considered.
            - If 'auto', then ``max_features`` = sqrt(n_features).
            - If 'sqrt', then ``max_features`` = sqrt(n_features).
            - If 'log2', then ``max_features`` = log2(n_features).
            - If None, then ``max_features`` = n_features considering all features in random order.

        Note: the search for a split does not stop until at least
        one valid partition of the node samples is found up to the point that
        all features have been considered,
        even if it requires to effectively inspect more than ``max_features`` features.

        `Decision Tree`: ``max_features`` = None and ``max_thresholds`` = None

        `Random Tree`: ``max_features`` < n_features and ``max_thresholds`` = None

    max_thresholds : int 1 or None, optional (default=None)
        Note: only to be used by Decision Forest

        The number of random thresholds to consider when looking for the best split at each node.

            - If 1, then consider 1 random threshold, based on the `Extreme Randomized Tree` formulation.
            - If None, then all thresholds, based on the mid-point of the node samples, are considered.

        `Extreme Randomized Trees (ET)`: ``max_thresholds`` = 1

        `Totally Randomized Trees`: ``max_features`` = 1 and ``max_thresholds`` = 1,
        very similar to `Perfect Random Trees (PERT)`.

    missing_values : str 'NMAR' or None, optional (default=None)
        Handling of missing values.

            - If 'NMAR' (Not Missing At Random), then during training: the split criterion considers missing values
              as another category and samples with missing values are passed to either the left or the right child
              depending on which option provides the best split,
              and then during testing: if the split criterion includes missing values,
              a missing value is dealt with accordingly (passed to left or right child),
              or if the split criterion does not include missing values,
              a missing value at a split criterion is dealt with by combining the results from both children
              proportionally to the number of samples that are passed to the children during training.
            - If None, an error is raised if one of the features has a missing value.
              An option is to use imputation (fill-in) of missing values prior to using the decision tree classifier.

    random_state : int or None, optional (default=None)

        A random state to control the pseudo number generation and repetitiveness of fit().

            - If int, random_state is the seed used by the random number generator;
            - If None, the random number generator is seeded with the current system time.

    Attributes
    ----------

    n_outputs_ : int
        The number of outputs (multi-output).

    classes_ : list of variable size arrays, shape = [n_classes for each output]
        The classes labels for each output.

    n_classes_ : list of int
        The number of classes for each output.

    n_features_ : int
        The number of features.

    max_features_ : int
        The inferred value of max_features.

    tree_ : tree object
        The underlying estimator.

    feature_importances_ : array, shape = [n_features]
        The feature importances. The higher, the more important the
        feature. The importance of a feature is computed as the (normalized)
        total reduction of the criterion brought by that feature.
    """

    # We use 'class_balance' as the hyperparameter name instead of 'class_weight'
    # The “class_weight” hyperparameter name is recognized by 'check_estimator()'
    # and the test “check_class_weight_ classifiers()” is performed that uses the
    # dict parameter and requires for a decision tree the “min_weight_fraction_leaf”
    # hyperparameter to be implemented to pass the test.

    def __init__(self,
                 class_balance='balanced',
                 max_depth=None,
                 max_features=None,
                 max_thresholds=None,
                 missing_values=None,
                 random_state=None):
        """ Create a new decision tree classifier and initialize it with hyperparameters.
        """

        # Hyperparameters
        self.class_balance = class_balance
        self.max_depth = max_depth
        self.max_features = max_features
        self.max_thresholds = max_thresholds
        self.missing_values = missing_values

        # Random Number Generator
        self.random_state = random_state

        return

    def fit(self, X, y):
        """ Build a decision tree classifier from the training data.

        Parameters
        ----------
        X : array, shape = [n_samples, n_features]
            The training input samples.

        y : array, shape = [n_samples] or [n_samples, n_outputs]
            The target class labels corresponding to the training input samples.

        Returns
        -------
        self : object
            Returns self.
        """

        # Check and prepare data
        # ----------------------

        # Check X, y

        if self.missing_values == 'NMAR':
            X, y = check_X_y(X, y, dtype=np.float64, order="C", force_all_finite='allow-nan', multi_output=True)
        else:
            X, y = check_X_y(X, y, dtype=np.float64, order="C", multi_output=True)

        n_samples, self.n_features_ = X.shape

        # Handle multi-outputs
        if y.ndim == 1:  # 2D format for single-output and multi-output
            y = np.reshape(y, (-1, 1))
        self.n_outputs_ = y.shape[1]

        if y.shape[0] != n_samples:
            raise ValueError("Mismatch: n_outputs, n_features and n_samples.")

        self.classes_ = []  # lists with an element for each output
        self.n_classes_ = np.zeros(self.n_outputs_, dtype=np.uint)
        y_int = np.zeros(y.shape, dtype=np.int)  # make sure y is integer
        for o in range(self.n_outputs_):  # process each output independently
            o_classes = unique_labels(y[:, o])  # Keep to raise required ValueError tested by 'check_estimator()'
            o_classes, y_int[:, o] = np.unique(y[:, o], return_inverse=True)  # Encode y from classes to integers
            self.classes_.append(o_classes)
            self.n_classes_[o] = o_classes.shape[0]
        if self.n_outputs_ == 1:
            self.classes_ = reduce(operator.concat, self.classes_)

        # Calculate class weights for each output separately
        # so that n_samples == sum of all weighted samples
        # Note that scikit-learn provides: 'compute_class_weight()' and 'compute_sample_weight()'
        # which multiplies the sample_weights of each output together to a single sample_weight
        # for multi-output (single model).

        # we use max(n_classes_) to create a nice 2D array to hold the class weights
        # as the number of classes can be different for different outputs
        class_weight = np.ones(shape=(self.n_outputs_, max(self.n_classes_)), dtype=np.float64)
        if self.class_balance is not None:
            if isinstance(self.class_balance, str):
                if self.class_balance in ['balanced']:
                    for o in range(self.n_outputs_):  # process each output independently
                        # The 'balanced' mode uses the values of y to
                        # automatically adjust weights inversely proportional
                        # to class frequencies in the input data.
                        mean_samples_per_class = y_int[:, o].shape[0] / self.n_classes_[o]
                        class_weight[o, :self.n_classes_[o]] = mean_samples_per_class / np.bincount(y_int[:, o])
                else:
                    raise ValueError("class_balance: unsupported string \'%s\', "
                                     "only 'balanced' is supported."
                                     % self.class_balance)
            else:
                raise TypeError("class_balance: %s is not supported."
                                % self.class_balance)

        # Check hyperparameters (here, not in __init__)

        # max depth

        if self.max_depth is not None:
            if not isinstance(self.max_depth, (numbers.Integral, np.integer)):
                raise TypeError("max_depth: must be an integer.")

        max_depth = self.max_depth if self.max_depth is not None else (2 ** 31) - 1

        if max_depth < 1:
            raise ValueError("max_depth: %s < 1, "
                             "but a decision tree requires to have at least a root node."
                             % max_depth)

        # max features

        if self.max_features is not None:
            if isinstance(self.max_features, str):
                if self.max_features in ['auto', 'sqrt']:
                    max_features = max(1, int(np.sqrt(self.n_features_)))
                elif self.max_features in ['log2']:
                    max_features = max(1, int(np.log2(self.n_features_)))
                else:
                    raise ValueError("max_features: unsupported string \'%s\', "
                                     "only 'auto', 'sqrt' and 'log2' are supported."
                                     % self.max_features)
            elif isinstance(self.max_features, (numbers.Integral, np.integer)):
                if self.max_features > 0:
                    max_features = self.max_features
                else:
                    raise ValueError("max_features: %s < 1, "
                                     "but a spit requires to consider a least 1 feature."
                                     % self.max_features)
            elif isinstance(self.max_features, (numbers.Real, np.float)):
                if self.max_features > 0.0:
                    if self.max_features <= 1.0:
                        max_features = max(1,
                                           min(int(self.max_features * self.n_features_),
                                               self.n_features_))
                    else:
                        raise ValueError("max_features: %s > 1.0, "
                                         "only floats <= 1.0 are supported."
                                         % self.max_features)
                else:
                    raise ValueError("max_features: %s <= 0.0, "
                                     "only floats > 0.0 are supported."
                                     % self.max_features)
            else:
                raise TypeError("max_features: %s is not supported, "
                                "only 'None', strings: 'auto', 'sqrt', 'log2', integers and floats are supported."
                                % self.max_features)
        else:
            max_features = self.n_features_

        if not (0 < max_features <= self.n_features_):
            raise ValueError("max_features: %s not in (0, n_features]"
                             % max_features)

        self.max_features_ = max_features

        # max thresholds

        max_thresholds = None
        if self.max_thresholds is not None:
            if isinstance(self.max_thresholds, (numbers.Integral, np.integer)):
                if self.max_thresholds == 1:
                    max_thresholds = 1
                else:
                    raise ValueError("max_thresholds: %s != 1, "
                                     "only 1 is supported."
                                     % self.max_thresholds)
            else:
                raise TypeError("max_thresholds: %s is not supported, "
                                "only 'None' and '1' are supported."
                                % self.max_thresholds)
        else:
            max_thresholds = 0

        # missing values

        if self.missing_values is not None:
            if isinstance(self.missing_values, str):
                if self.missing_values in ['NMAR']:
                    missing_values = self.missing_values
                else:
                    raise ValueError("missing_values: unsupported string \'%s\', "
                                     "only 'NMAR' is supported."
                                     % self.missing_values)
            else:
                raise TypeError("missing_values: %s is not supported."
                                % self.missing_values)
        else:
            missing_values = 'None'
            if np.any(np.isnan(X)):
                raise ValueError("missing_values: None, but X contains np.NaN.")

        # Random Number Generator

        random_state = RandomState(self.random_state)

        # Build decision tree
        # -------------------

        # Initialize the tree builder
        builder = DepthFirstTreeBuilder(self.n_outputs_, self.n_classes_, max(self.n_classes_), self.n_features_,
                                        n_samples, class_weight, max_depth, max_features, max_thresholds,
                                        missing_values, random_state)

        # Create an empty tree
        self.tree_ = Tree(self.n_outputs_, self.n_classes_, self.n_features_)

        # Build a decision tree from the training data X, y

        # workaround cython not supporting read-only memory view
        # https://github.com/cython/cython/issues/1605
        if not X.flags.writeable:
            X = X.copy()

        builder.build(self.tree_, X, y_int)

        # Return the classifier
        return self

    def predict(self, X):
        """ Predict classes for the test data.

        Parameters
        ----------
        X : array, shape = [n_samples, n_features]
            The test input samples.

        Returns
        -------
        y : array, shape = [n_samples] or [n_samples, n_outputs]
            The predicted classes for the test input samples.
        """

        # Check that fit has been called
        check_is_fitted(self, ['tree_'])

        # Check X
        if self.missing_values == 'NMAR':
            X = check_array(X, dtype=np.float64, order="C", force_all_finite='allow-nan')
        else:
            X = check_array(X, dtype=np.float64, order="C")

        n_samples = X.shape[0]
        n_classes_max = max(self.n_classes_)

        # Predict classes probabilities
        class_probablities = self.predict_proba(X)
        # Handle single-output and multi-outputs formatting
        # 2D format for single-output and multi-output
        class_probablities = np.reshape(class_probablities, (-1, self.n_outputs_, n_classes_max))

        # Handle multi-outputs formatting
        y = []
        if self.n_outputs_ == 1:
            # Determine class based on highest classes probabilities
            predictions = np.argmax(class_probablities[:, 0], axis=1)
            # Decode y back from integers to classes
            y = self.classes_.take(predictions, axis=0)
        else:
            for o in range(self.n_outputs_):
                # Determine class based on highest classes probabilities
                predictions = np.argmax(class_probablities[:, o], axis=1)
                # Decode y back from integers to classes
                y.append(self.classes_[o].take(predictions, axis=0))
            y = np.array(y)
            y = np.reshape(y.transpose(), (-1, self.n_outputs_)) # 2D format for multi-output

        return y

    def predict_proba(self, X):
        """ Predict classes probabilities for the test data.

        Parameters
        ----------
        X : array, shape = [n_samples, n_features]
            The test input samples.

        Returns
        -------
        p : array, shape = [n_samples x n_classes] or [n_samples x n_outputs x n_classes_max]
            The predicted classes probabilities for the test input samples.
        """

        # Check that fit has been called
        check_is_fitted(self, ['tree_'])

        # Check X
        if self.missing_values == 'NMAR':
            X = check_array(X, dtype=np.float64, order="C", force_all_finite='allow-nan')
        else:
            X = check_array(X, dtype=np.float64, order="C")

        n_features = X.shape[1]
        if self.n_features_ != n_features:
            raise ValueError("X: number of features %s != number of features of the model %s, "
                             "must match."
                             % (n_features, self.n_features_))

        # Predict classes probabilities

        # workaround cython not supporting read-only memory view
        # https://github.com/cython/cython/issues/1605
        if not X.flags.writeable:
            X = X.copy()

        proba = self.tree_.predict(X)

        # Handle single-output and multi-outputs formatting
        n_classes_max = max(self.n_classes_)
        if self.n_outputs_ == 1:
            proba = np.reshape(proba, (-1, self.n_classes_[0]))
        else:
            proba = np.reshape(proba, (-1, self.n_outputs_, n_classes_max))

        return proba


    def score(self, X, y):
        """Returns the mean accuracy on the given test data and labels.

        sklearn has no metrics support for "multiclass-multioutput" format,
        therefore we implement our own score() here

        In multi-label classification, this is the subset accuracy
        which is a harsh metric since you require for each sample that
        each label set be correctly predicted.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Test samples.

        y : array-like, shape = (n_samples) or (n_samples, n_outputs)
            True labels for X.

        Returns
        -------
        score : float
            Mean accuracy of self.predict(X) wrt. y.

        """

        y_pred = self.predict(X)

        # Handle single-output and multi-outputs formatting
        y = y.ravel()
        y_pred = y_pred.ravel()

        # No metrics support "multiclass-multioutput" format
        # y_type, y, y_pred = _check_targets(y, y_pred)
        check_consistent_length(y, y_pred)

        score = np.average(y == y_pred)

        return score


    @property
    def feature_importances_(self):
        """ Get feature importances from the decision tree.
        """

        # Check that fit has been called
        check_is_fitted(self, ['tree_'])

        # Calculate feature importances for the decision tree
        return self.tree_.calculate_feature_importances()

    def export_graphviz(self, feature_names=None, class_names=None, rotate=False):
        """ Export of a decision tree in GraphViz dot format.

        Parameters
        ----------
        feature_names : list of str, optional (default=None)
            Names of each of the features.

        class_names : list of str, optional (default=None)
            Names of each of the classes in ascending numerical order.
            Classes are represented as integers: 0, 1, ... (n_classes-1).
            If y consists of class labels, those class labels need to be provided as class_names again.

        rotate : bool, optional (default=False)
            When set to True, orient tree left to right rather than top-down.

        Returns
        -------
        dot_data : str
            String representation of the decision tree classifier in GraphViz dot format.
        """

        def process_tree_recursively(tree, node_id):
            """ Process tree recursively node by node and provide GraphViz dot format for node."""

            # Current node
            left_child = tree.get_node_left_child(node_id)
            right_child = tree.get_node_right_child(node_id)
            feature = tree.get_node_feature(node_id)
            NA = tree.get_node_NA(node_id)
            threshold = tree.get_node_threshold(node_id)
            histogram = tree.get_node_histogram(node_id)
            impurity = tree.get_node_impurity(node_id)

            # Prediction
            n = sum(histogram[0]) # use histogram from 1st output, all the same
            p_c = [0.0]*tree.get_n_outputs()
            c = [0]*tree.get_n_outputs()
            for o in range(tree.get_n_outputs()):
                p_c[o] = histogram[o] / n
                c[o] = np.argmax(p_c[o])
                # formatting
                p_c[o] = [int(x) if x % 1 == 0 else round(float(x), 2) for x in p_c[o]]

            # Node color and intensity based on classification and impurity
            classes_combination = c[0]
            for o in range(1, tree.get_n_outputs()):
                classes_combination += tree.get_n_classes()[o-1] * c[o]
            (r, g, b) = rgb_LUT[classes_combination]
            max_impurity = [0.0]*tree.get_n_outputs()
            for o in range(0, tree.get_n_outputs()):
                max_impurity[o] = 1.0 - (1.0 / tree.get_n_classes()[o])
            max_impurity_avrg = sum(max_impurity) / tree.get_n_outputs()
            alpha = int(255 * (max_impurity_avrg - impurity) / max_impurity_avrg)
            color = '#' + ''.join('{:02X}'.format(a) for a in [r, g, b, alpha])  # #RRGGBBAA hex format

            # Leaf node
            if left_child == 0:
                # leaf nodes do no have any children
                # so we only need to test for one of the children

                # Node
                dot_data.write('%d [label=\"' % node_id)
                for o in range(tree.get_n_outputs()):
                    dot_data.write('%s\\n' % p_c[o][:tree.get_n_classes()[o]])
                if tree.get_n_outputs() == 1:
                    class_name = class_names[c[0]] if class_names is not None else "%d" % c[0]
                    dot_data.write('%s' % class_name)
                else:
                    for o in range(tree.get_n_outputs()):
                        class_name = class_names[o][c[o]] if class_names is not None else "%d" % c[o]
                        dot_data.write('%s\\n' % class_name)
                dot_data.write('\", fillcolor=\"%s\"] ;\n' % color)

            # Split node
            else:

                # Order children nodes by predicted classes (and their probabilities)
                # Switch left_child with right_child and
                # modify test feature <= threshold (default) vs feature > threshold accordingly

                order = True
                test_type = 0  # 0: feature <= threshold (default)
                # 1: feature >  threshold, when left and right children are switched

                change = False
                if order:
                    # Order children based on prediction from first output
                    # Left Child Prediction
                    lc_histogram = tree.get_node_histogram(left_child)[0]
                    lc_c = np.argmax(lc_histogram)
                    lc_n = sum(lc_histogram)
                    lc_p_c = lc_histogram[lc_c] / lc_n
                    # Right Child Prediction
                    rc_histogram = tree.get_node_histogram(right_child)[0]
                    rc_c = np.argmax(rc_histogram)
                    rc_n = sum(rc_histogram)
                    rc_p_c = rc_histogram[rc_c] / rc_n
                    # Determine if left_child and right_child should be switched based on predictions
                    if lc_c > rc_c:  # assign left child to lower class index
                        change = True
                    elif lc_c == rc_c:  # if class indices are the same for left and right children
                        if lc_c == 0:  # for the first class index = 0
                            if lc_p_c < rc_p_c:  # assign left child to higher class probability
                                change = True
                        else:  # for all other class indices > 0
                            if lc_p_c > rc_p_c:  # assign left child to lower class probability
                                change = True
                    if change:
                        test_type = 1
                        left_child, right_child = right_child, left_child

                feature_name = feature_names[feature] if feature_names is not None else "X[%d]" % feature
                threshold = round(threshold, 3)

                # Edge width based on (weighted) number of samples used for training
                # use histogram from 1st output, all the same
                n_root = sum(tree.get_node_histogram(0)[0])  # total number of samples used for training
                n_left_child = sum(tree.get_node_histogram(left_child)[0]) / n_root  # normalized
                n_right_child = sum(tree.get_node_histogram(right_child)[0]) / n_root

                max_width = 10

                # Node
                dot_data.write('%d [label=\"' % node_id)
                # - feature
                dot_data.write('%s' % feature_name)
                # - threshold
                if not np.isnan(threshold):
                    if test_type == 0:
                        dot_data.write(' <= %s' % threshold)
                    else:  # test_type == 1
                        dot_data.write(' > %s' % threshold)
                # - NA
                if NA != -1:
                    if change == False:
                        if NA == 0:  # left
                            dot_data.write(' NA')
                        if NA == 1:  # right
                            dot_data.write(' not NA')
                    else:  # test_type == 1
                        if NA == 0:  # right
                            dot_data.write(' not NA')
                        if NA == 1:  # left
                            dot_data.write(' NA')

                # - histogram
                if node_id == 0:  # Root node with legend
                    dot_data.write('\\np(class) = ')
                    for o in range(tree.get_n_outputs()):
                        dot_data.write('%s\\n' % p_c[o][:tree.get_n_classes()[o]])
                    dot_data.write('class, n = %s' % int(round(n, 0)))
                else:
                    dot_data.write('\\n')
                    if tree.get_n_outputs() == 1:
                        dot_data.write('%s' % p_c[0][:tree.get_n_classes()[0]])
                    else:
                        for o in range(tree.get_n_outputs()):
                            dot_data.write('%s\\n' % p_c[o][:tree.get_n_classes()[o]])
                dot_data.write('\", fillcolor=\"%s\"] ;\n' % color)

                # Edges
                # - left child
                dot_data.write('%d -> %d [penwidth=%f' % (node_id, left_child, max_width * n_left_child))
                if node_id == 0:  # Root node with legend
                    dot_data.write(', headlabel="True", labeldistance=2.5, labelangle=%d' % (-45 if rotate else 45))
                dot_data.write('] ;\n')
                # - right child
                dot_data.write('%d -> %d [penwidth=%f] ;\n' % (node_id, right_child, max_width * n_right_child))
                # layout problems with legend true and false depending on tree size
                # no need to define false when true is defined

                # process the children's sub trees recursively
                process_tree_recursively(tree, left_child)
                process_tree_recursively(tree, right_child)

            return

        def create_rgb_LUT(n_classes):
            """ Create a rgb color look up table (LUT) for all classes.
            """

            # Define rgb colors for the different classes
            # with (somewhat) max differences in hue between nearby classes

            # Number of iterations over the grouping of 2x 3 colors
            n_classes = max(n_classes, 1)  # input check > 0
            n = ((n_classes - 1) // 6) + 1  # > 0

            # Create a list of offsets for the grouping of 2x 3 colors
            # that (somewhat) max differences in hue between nearby classes
            offset_list = [0]  # creates pure R G B - Y C M colors
            d = 128
            n_offset_levels = int(scipy.log2(n - 1) + 1) if n > 1 else 1  # log(0) not defined
            n_offset_levels = min(n_offset_levels, 4)  # limit number of colors to 96
            for i in range(n_offset_levels):
                # Create in between R G B Y C M colors
                # in a divide by 2 pattern per level
                # i=0: + 128,
                # i=1: +  64, 192,
                # i=2: +  32, 160, 96, 224,
                # i=3: +  16, 144, 80, 208, 48, 176, 112, 240
                # abs max i=7 with + 1 ...
                offset_list += ([int(offset + d) for offset in offset_list])
                d /= 2

            # If there are more classes than colors
            # then the offset_list is duplicated,
            # which assigns the same colors to different classes
            # but at least to the most distance classes
            length = len(offset_list)
            if n > length:
                offset_list = int(1 + scipy.ceil((n - length) / length)) * offset_list

            rgb_LUT = []
            for i in range(n):
                # Calculate grouping of 2x 3 rgb colors R G B - Y C M
                # that (somewhat) max differences in hue between nearby classes
                # and makes it easy to define other in between colors
                # using a simple linear offset
                # Based on HSI to RGB calculation with I = 1 and S = 1
                offset = offset_list[i]
                rgb_LUT.append((255, offset, 0))  # 0 <= h < 60 RED ...
                rgb_LUT.append((0, 255, offset))  # 120 <= h < 180 GREEN ...
                rgb_LUT.append((offset, 0, 255))  # 240 <= h < 300 BLUE ...
                rgb_LUT.append((255 - offset, 255, 0))  # 60 <= h < 120 YELLOW ...
                rgb_LUT.append((0, 255 - offset, 255))  # 180 <= h < 240 CYAN ...
                rgb_LUT.append((255, 0, 255 - offset))  # 300 <= h < 360 MAGENTA ...

            return rgb_LUT

        # Check that fit has been called
        check_is_fitted(self, ['tree_'])

        # Handle single-output and multi-output formatting

        if class_names is not None:
            if isinstance(class_names, list) or isinstance(class_names, np.ndarray):
                if self.tree_.get_n_outputs() == 1:
                    class_names = np.array(class_names).ravel()
            else:
                raise TypeError("class_names type: %s is not supported." % type(class_names))


        dot_data = StringIO()

        dot_data.write('digraph Tree {\n')
        dot_data.write(
            'node [shape=box, style=\"rounded, filled\", color=\"black\", fontname=helvetica, fontsize=14] ;\n')
        dot_data.write('edge [fontname=helvetica, fontsize=12] ;\n')

        # Rotate (default: top-down)
        if rotate:
            dot_data.write('rankdir=LR ;\n')  # left-right orientation

        # Define rgb colors for the different classes over all outputs
        n_classes_combinations = np.prod([self.tree_.get_n_classes()[o] for o in range(self.tree_.get_n_outputs())])
        rgb_LUT = create_rgb_LUT(n_classes_combinations)

        # Process the tree recursively
        process_tree_recursively(self.tree_, 0)  # root node = 0

        dot_data.write("}")

        return dot_data.getvalue()

    def export_text(self):
        """ Export of a decision tree in a simple text format.

        Returns
        -------
        data : str
            String representation of the decision tree classifier in a simple text format.
        """

        def process_tree_recursively(tree, node_id):
            """ Process tree recursively node by node and provide simple text format for node.
            """

            # Current node
            left_child = tree.get_node_left_child(node_id)
            right_child = tree.get_node_right_child(node_id)
            feature = tree.get_node_feature(node_id)
            NA = tree.get_node_NA(node_id)
            threshold = round(tree.get_node_threshold(node_id), 3)
            histogram = [[int(x) if x % 1 == 0 else round(float(x), 2) for x in tree.get_node_histogram(node_id)[o][:tree.get_n_classes()[o]]]
                         for o in range(tree.get_n_outputs())]

            # Leaf node
            if left_child == 0:
                # leaf nodes do no have any children
                # so we only need to test for one of the children

                data.write('%d ' % node_id)
                for o in range(tree.get_n_outputs()):
                    data.write('%s' % histogram[o])
                data.write('; ' % histogram[o])

            # Split node
            else:

                data.write('%d' % node_id)
                data.write(' X[%d]' % feature)
                if not np.isnan(threshold):
                    data.write('<=%s' % threshold)
                if NA == 0:
                    data.write(' NA')
                if NA == 1:
                    data.write(' not NA')
                data.write(' ')
                for o in range(tree.get_n_outputs()):
                    data.write('%s' % histogram[o])
                data.write('; ' % histogram[o])

                data.write('%d->%d; ' % (node_id, left_child))
                data.write('%d->%d; ' % (node_id, right_child))

                # process the children's sub trees recursively
                process_tree_recursively(tree, left_child)
                process_tree_recursively(tree, right_child)

            return

        # Check that fit has been called
        check_is_fitted(self, ['tree_'])

        data = StringIO()

        # Process the tree recursively
        process_tree_recursively(self.tree_, 0)  # root node = 0

        return data.getvalue()
