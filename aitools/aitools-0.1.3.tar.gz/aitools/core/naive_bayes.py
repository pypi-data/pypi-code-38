import math


INDEX_LABELS = 0
INDEX_FEATURE_FREQUENCY = 1
INDEX_LABEL_FREQUENCY = 2
INDEX_LABEL_FEATURES = 3


class NaiveBayes:

    def __init__(self, independent_features, dependent_feature):

        self.independent_features = independent_features
        self.dependent_feature = dependent_feature
        self.probabilities = []

    def build(self):

        attributes = get_required_attributes(self.independent_features, self.dependent_feature)
        self.probabilities = features_probabilities(
            attributes[INDEX_LABELS],
            attributes[INDEX_FEATURE_FREQUENCY],
            attributes[INDEX_LABEL_FREQUENCY],
            attributes[INDEX_LABEL_FEATURES]
        )

    def predict(self, independent_features):

        probability = {}

        for features in independent_features:
            feature = tuple(features)
            for meta in self.probabilities:
                if meta in features:
                    for prob in self.probabilities[meta]:
                        probability[feature] = {} if feature not in probability else probability[feature]
                        probability[feature][prob] = 0 \
                            if prob not in probability[feature] \
                            else probability[feature][prob] + self.probabilities[meta][prob]

        return probability


def get_required_attributes(independent_features, dependent_feature):
    return (
        feature_metric(zip(independent_features, dependent_feature)),
        frequency_metric(independent_features),
        frequency_metric(dependent_feature),
        features_metric(zip(independent_features, dependent_feature)),
    )


def feature_metric(features):

    metric = {}

    for independent, dependent in features:

        metric[dependent] = [] if dependent not in metric else metric[dependent]

        for feature in independent:
            metric[dependent].append(feature)

    return metric


def frequency_metric(features):

    metric = {}

    for feature in features:

        if isinstance(feature, list):
            for f in feature:
                metric[f] = 1 if f not in metric else metric[f] + 1
        else:
            metric[feature] = 1 if feature not in metric else metric[feature] + 1

    return metric


def features_metric(features):

    metric = {}

    for independent, dependent in features:

        metric[dependent] = [] if dependent not in metric else metric[dependent]
        metric[dependent].append(independent)

    return metric


def features_probabilities(labels, feature_frequency, label_frequency, label_features):

    probabilities = {}

    for feature in feature_frequency:
        for label in labels:

            probability = 0
            probabilities[feature] = {} if feature not in probabilities else probabilities[feature]

            # # probability_feature_label = \
            # #     labels[label].count(feature) / len(labels[label])
            #
            # probability_feature_label = \
            #     sum(features.count(feature) for features in label_features[label]) / feature_frequency[feature]
            #
            # # probability_feature = \
            # #     feature_frequency[feature] / sum(feature_frequency.values())
            #
            # probability_feature = \
            #     labels[label].count(feature) / len(labels[label])
            #
            # probability_label = \
            #     label_frequency[label] / sum(label_frequency.values())

            probability_label_feature = \
                sum(1 if feature in features else 0 for features in label_features[label]) / len(label_features[label])

            probability_label = \
                label_frequency[label] / sum(label_frequency.values())

            probability_feature = \
                labels[label].count(feature) / len(labels[label])

            if probability_feature != 0:
                probability = (probability_label_feature * probability_feature) / probability_label
                print(probability)

            probabilities[feature].update({label: probability})

    return probabilities
