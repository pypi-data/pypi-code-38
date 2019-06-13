from dtrees.algorithms.learn_tree import *
from dtrees.core.pruning import *
from pandas import DataFrame, Series
from numpy import nan
from numpy import random as rnd
import pickle


class DecisionTree():
    """
    Дерево решений. Позволяет строить дерево одним из общих алгоритмов:
    ID3, C4.5, либо построить дерево с одним из доступных критериев ветвления,
    вызвав функцию learn.
    Возможные критерии :
        entropy
        Gini
        D
        Tsallis
        Renyi

    Для обучения с помощью learn, необходимо передать параметры в виде словаря.
    Доступные параметры:
        criterion
        alpha
        minSamples
    """
    criterions = ['entropy', 'Gini', 'D', 'Tsallis', 'Renyi']

    def __init__(self):
        self.tree = None
        self.data = None
        self.attrribute_properties = {}
        self.attribute_types = {}

    def _setAttrributeProperties(self, data, as_categorial=()):
        for attr in data:
            attrType = data[attr].dtype
            if attrType in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']:
                if attr in as_categorial:
                    self.attrribute_properties[attr] = set(filter(lambda x: x not in [None, nan], data[attr].unique()))
                    self.attribute_types[attr] = 1
                else:
                    self.attribute_types[attr] = 0
            elif isinstance(attrType, object) or (attr in as_categorial):
                self.attrribute_properties[attr] = set(filter(lambda x: x not in [None, nan], data[attr].unique()))
                self.attribute_types[attr] = 1
            else:
                raise Exception("Unknown attribute type")

    def ID3(self, data, target, as_categorial=()):
        """
        :param data: pandas DataFrame
        :param target: string, target column
        :param as_categorial: attributes considered as categorical
        """
        if isinstance(data, DataFrame):
            if data.empty:
                raise BaseException('Empty data')
            self._setAttrributeProperties(data, as_categorial)
            tree = Tree(data=data, target=target, attrProp=self.attrribute_properties, attrTypes=self.attribute_types)
            self.tree = tree._id3_(data, currId=0, parentId=-1)

    def C45(self, data, target, as_categorial=(), pruneLevel=0, maxDepth=-1):
        """
        :param data: pandas DataFrame
        :param target: string, target column
        :param as_categorial: attributes considered as categorical
        :param pruneLevel: int, 0..5
        """
        if isinstance(data, DataFrame):
            if data.empty:
                raise BaseException('Empty data')
            self._setAttrributeProperties(data, as_categorial)
            self.data = data.copy()
            tree = Tree(data=self.data, target=target, attrProp=self.attrribute_properties,
                        attrTypes=self.attribute_types)
            self.tree = tree._c45_(self.data, currId=0, parentId=-1)
            N = self.data.shape[0]
            params = {'pruneLevel': pruneLevel}
            self._pruning_(N, params)
            del self.tree.data
            del self.data

    def learn(self, data, target, as_categorial=(), params=None):
        """
        :param data: pandas DataFrame
        :param target: string, target column
        :param as_categorial: attributes considered as categorical
        params = {
            criterion : string, one of available criterions,
            alpha : list of any numbers except 1,
            minSamples : float, number of min samples to split node
            pruneLevel : pruning level in range 0..5,
            maxDepth : max depth of tree
        }
        """
        if isinstance(data, DataFrame):
            if data.empty:
                raise BaseException('Empty data')
            if 'criterion' in params:
                if params['criterion'] not in self.criterions:
                    raise Exception("Unknown criterion {}".format(params['criterion']))
                if params['criterion'] == 'Tsallis' or params['criterion'] == 'Renyi':
                    if 'alpha' in params:
                        if params['alpha'] == 1:
                            raise Exception("alpha = 1 is unacceptable value for Tsallis and Renyi entropy")
            else:
                params['criterion'] = 'entropy'
            self._setAttrributeProperties(data, as_categorial)
            self.data = data.copy()
            N = self.data.shape[0]
            tree = Tree(data=self.data, target=target, attrProp=self.attrribute_properties,
                        attrTypes=self.attribute_types, params=params)
            self.tree = tree._c45_(self.data, currId=0, parentId=-1)
            # Pruning
            self._pruning_(N, params)
            del self.tree.data
            del self.data

    def _pruning_(self, N, params):
        if 'pruneLevel' in params:
            pruneLevel = params['pruneLevel']
        else:
            pruneLevel = 2
        if 'minSamples' in params:
            minSamples = float(params['minSamples'])
            if minSamples < 1:
                # percent
                minSamples *= N
        else:
            minSamples = 2
        if 'maxDepth' in params:
            maxDepth = params['maxDepth']
        else:
            maxDepth = -1
        if pruneLevel == 1:
            errorBasedPruning(self.tree)
        elif pruneLevel == 2:
            errorBasedPruning(self.tree)
            pruneMinSamples(self.tree, minSamples)
        elif pruneLevel == 3:
            errorBasedPruning(self.tree)
            pruneMinSamples(self.tree, minSamples)
            self.tree._pruneSameChild_()
        elif pruneLevel == 4:
            self.tree._pruneSameChild_()
            errorBasedPruning(self.tree)
            prue_1 = pruneMinSamples(self.tree, minSamples)
            prue_2 = self.tree._pruneSameChild_()
            while prue_1 or prue_2:
                prue_1 = pruneMinSamples(self.tree, minSamples)
                prue_2 = self.tree._pruneSameChild_()
        elif pruneLevel == 5:
            if maxDepth > 0:
                pruneMaxDepth(self.tree, maxDepth)
            self.tree._pruneSameChild_()
            pruneMinSamples(self.tree, minSamples)

    def gridSearch(self, data, target, params, as_categorical=()):
        """
        Решетчатый поиск с k-блочной проверкой
        :param data: pandas DataFrame
        :param target: target attribute, String
        :param params: dictionary
        :param as_categorical: attributes considered as categorical
        :return: best accuracy, best params

        params = {
            K : int (k fold),
            trainSize : part of train examples 0..1,
            criterion : string, one of available criterions,
            alpha : list of any numbers except 1,
            minSamples : list of min samples,
            pruneLevel : list of prune levels 0..5,
            maxDepth : list of max depth (if pruneLevel = 5)
        }
        """
        if 'K' in params:
            K = params['K']
            del params['K']
        else:
            K = 3
        if 'trainSize' in params:
            ts = params['trainSize']
            del params['trainSize']
        else:
            ts = 0.85
        N = int(data.shape[0] * ts)
        if 'criterion' not in params:
            criterions = ['entropy']
        else:
            criterions = params['criterion']
        if 'alpha' not in params:
            alphas = [2]
        else:
            alphas = params['alpha']
        if 'minSamples' not in params:
            minSamples = [2]
        else:
            minSamples = params['minSamples']
        if 'pruneLevel' not in params:
            pruneLevels = [2]
        else:
            pruneLevels = params['pruneLevel']
        if 'maxDepth' in params:
            maxDepth_ = params['maxDepth']
        else:
            maxDepth_ = [-1]

        accuracy__, params__ = [], []
        ind = np.arange(0, data.shape[0], 1).astype(np.int)
        for C in criterions:
            for a in alphas:
                for ms in minSamples:
                    for pl in pruneLevels:
                        for d in maxDepth_:
                            averAcc = 0
                            params_ = {
                                'criterion': C,
                                'alpha': a,
                                'pruneLevel': pl,
                                'minSamples': ms,
                                'maxDepth': d
                            }
                            # K-Fold validation
                            for _ in range(K):
                                try:
                                    trainInd = rnd.choice(ind, N, replace=False)
                                    testInd = [i for i in ind if i not in trainInd]
                                    train = data.loc[trainInd]
                                    test = data.loc[testInd]
                                    dt = DecisionTree()
                                    dt.learn(train, target, as_categorical, params=params_)
                                    Y = test[target].values
                                    res = dt.predict(test, vector=True)
                                    acc = sum(res == Y) / test.shape[0]
                                    averAcc += acc
                                except Exception as ex:
                                    print(ex)
                            averAcc /= K
                            accuracy__.append(averAcc)
                            params__.append(params_)
        bestParamsInd = np.argmax(accuracy__)
        return round(accuracy__[bestParamsInd], 3), params__[bestParamsInd]

    def predict(self, example, vector=True):
        """
        :param example: pandas DataFrame or Series
        :param vector: boolean. If true res output is Series, else DataFrame with probabiities
        :return: result of prediction
        """
        if self.tree._initialized:
            res = None
            if isinstance(example, DataFrame):
                rootNode = self.tree.getNode(0)
                res = pd.DataFrame(columns=self.tree.targetLbls)
                for _, ex in example.iterrows():
                    y = self.tree._predict_(ex, rootNode)
                    res = res.append(y, ignore_index=True)
            elif isinstance(example, Series):
                rootNode = self.tree.getNode(0)
                res = pd.DataFrame(self.tree._predict_(example, rootNode), index=[0])
            if vector:
                res = res.idxmax(axis=1)
                return res
            else:
                return res

    def save(self, name):
        """
        :param name: output name
        """
        with open(name, 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()

    def load(self, name):
        """
        :param name: serialized decisioin tree
        """
        with open(name, 'rb') as f:
            dt = pickle.load(f)
            f.close()
        self.tree = dt.tree
        self.attribute_types = dt.attribute_types
        self.attrribute_properties = dt.attrribute_properties
