from aitools.utils import constant, util
from aitools.core.utils import word_stemmer


class NaiveBayes:

    def __init__(self, data_metric, regex):
        """

        :param data_metric:
        :param regex:
        """
        self.regex = regex
        self.data_metric = data_metric

        self.class_list = []
        self.feature_list = []
        self.class_count = []
        self.class_features = []

        self.probabilities = []

    def build(self):
        """

        """
        self.class_list, \
            self.feature_list, \
            self.class_count, \
            self.class_features = create_classification_corpus(self.data_metric, self.regex)

        self.probabilities = get_word_probabilities(self.class_list,
                                                    self.feature_list,
                                                    self.class_count,
                                                    self.class_features)

    def predict(self, speech):
        """
        :param speech: speech is the user input of which probability is needed
        :return: class with max probability
        """
        # return max(classify_naive_bayes(speech,
        #                                 self.probabilities,
        #                                 self.frame_class_list,
        #                                 self.regex).items(),
        #            key=operator.itemgetter(1))[0]

        return classify_naive_bayes(speech, self.probabilities, self.class_list, self.regex)


def create_classification_corpus(data_metric, regex):
    """
    :param data_metric:
    :param regex: regular expression for text extraction
    :return: tools require for classification engines
             df_class,df_words,df_class_count --- refer to ClassificationEngine.py for more details

    business logic behind init tools is written here, it basically loops around the
    entire data set and separate them into three different components
    """
    feature_count, classes, features, feature_set, class_features = {}, {}, {}, {}, {}
    stem = word_stemmer.WordStemmer()
    stop = set(constant.STOPWORDS)

    for c in list(set(data[-1] for data in data_metric)):
        classes[c] = []

    for data in data_metric:
        in_class = data[constant.INDEX_NEG_ONE]
        in_features = data[constant.INDEX_ZERO]
        in_features = in_features if isinstance(in_features, str) else ' '.join(in_features)
        features.update(feature_set)

        if in_class not in class_features:
            class_features[in_class] = [[]]
        else:
            class_features[in_class].append([])

        for w in util.tokenizer(regex, in_features.lower()):

            if w not in stop:
                stem_word = stem.stem(w)
                feature_set[stem_word] = 1 if stem_word not in feature_set else feature_set[stem_word] + 1
                class_features[in_class][len(class_features[in_class]) - 1].append(stem_word)
                classes[in_class].append(stem_word)

        feature_count[in_class] = 1 if in_class not in feature_count else feature_count[in_class] + 1

    return classes, features, feature_count, class_features


def get_all_features(in_features, regex):
    """

    :param in_features:
    :param regex:
    :return:
    """
    return [util.tokenizer(regex, f.lower()) if isinstance(f, str) else f for f in in_features]


def get_word_probabilities(df_class, df_word, df_class_count, frame_class_words):
    """
    :param frame_class_words:
    :param df_class: all Classes and words (grouped by classes) - dict
    :param df_word: all words and word frequencies - dict
    :param df_class_count: all classes and class frequencies - dict
    :return: every word with probability of classes(word can be in that particular class) - dict
    """
    probabilities = {}
    for w in df_word:
        for c in df_class:

            if w not in probabilities:
                probabilities[w] = {}

            probability_class_words = len([x for x in frame_class_words[c] if w in x]) / len(frame_class_words[c])
            probability_words = (df_class[c].count(w) / len(df_class[c]))
            probability_class = (df_class_count[c] / sum(df_class_count.values()))
            probability = 0 if probability_words == 0 else (
                                                               probability_class_words * probability_class) / probability_words
            probabilities[w].update({c: probability})

    return probabilities


def classify_naive_bayes(speech, probabilities, frame_class, regex):
    """

    :param speech:
    :param probabilities:
    :param frame_class:
    :param regex:
    :return:
    """
    tokens = util.prepare_tokens(speech, regex, set(constant.STOPWORDS), word_stemmer.WordStemmer())
    class_probabilities = {}
    classify = {}
    for c in frame_class:
        class_probabilities[c] = 0

    for meta in probabilities:
        if meta in tokens:
            for c in frame_class:
                class_probabilities[c] += probabilities[meta][c]

    for c in frame_class:
        classify[c] = class_probabilities[c]

    return class_probabilities
