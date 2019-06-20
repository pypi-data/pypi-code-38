import typing
import pandas
import re

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised
from numpy import float64, int64, isnan
from common_primitives import utils
from sklearn.feature_extraction.text import TfidfVectorizer

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame

class ColumnConditioner(object):

    def __init__(self, col, hps):
        self.data = col
        self.hps = hps

    def can_handle(self):
        clen = len(self.data)
        if clen == 0:
            return None
        failures = 0
        for x in self.data:
            try:
                self.converter(x)
            except ValueError:
                failures += 1
                if float(failures) / clen > 0.5:
                    return None
        return self

    def fit(self):
        self._tally()
        self._calculate_median()
        self._construct_dict()
        del(self.data)
        del(self.counts)
        del(self.total)
        return self

    def produce(self, data, colindex):

        def convert(x):
            try:
                x = self.converter(x)
                if isnan(x):
                    return self.median
                else:
                    return x
            except ValueError:
                return self.median

        # print("Converting column", col)
        data.iloc[:,colindex] = data.iloc[:,colindex].apply(convert)
        return data

    def _tally(self):
        self.counts = {}
        self.total = 0
        for x in self.data:
            self.total += 1
            try:
                self.counts[x] += 1
            except KeyError:
                self.counts[x] = 1

    def _calculate_median(self):
        values = []
        converted = {}
        first_total = 0
        for v in self.data:
            try:
                cv = self.converter(v)
                converted[v] = cv
                if not isnan(cv):
                    first_total += self.counts[v]
                    values.append(v)
            except ValueError:
                pass
        values = sorted(values, key=lambda x: converted[x])
        total = 0
#        print(values)
        self.median = 0
        for v in values:
            total += self.counts[v]
            if total >= first_total * 0.5:
                self.median = converted[v]
                break

    def _construct_dict(self):
        pass

    def update_metadata(self, data, ci):
       pass


class CategoricalConditioner(ColumnConditioner):
    def can_handle(self):
        if not any(type(x) is str for x in self.data):
            return None
        # TODO: Make this a hyperparameter
        if len(set(self.data)) > 20:
            return None
        return self

    def _calculate_median(self):
        pass

    def _construct_dict(self):
        keys = sorted(self.counts.keys(), reverse=True, key=lambda x: self.counts[x])
        self.dictionary = dict((keys[i], i+1) for i in range(len(keys)))

    def produce(self, data, colindex):
        def convert(x):
            try:
                return self.dictionary[x]
            except:
                return 0
        data.iloc[:,colindex] = data.iloc[:,colindex].apply(convert).astype(int)
        return data

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = int
        data.metadata = data.metadata.update_column(ci, mdata)


class IntegerConditioner(ColumnConditioner):
    def __init__(self, col, hps):
        super().__init__(col, hps)
        self.converter = int

    def produce(self, data, colindex):
        super().produce(data, colindex)
        data.iloc[:,colindex] = data.iloc[:,colindex].astype(int)
        return data

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = int
        data.metadata = data.metadata.update_column(ci, mdata)

    def can_handle(self):
        dtype = self.data.dtype
        if dtype == float or dtype == float64:
            return None
        elif dtype == int or dtype == int64:
            return self
        else:
            return super().can_handle()


class FloatConditioner(ColumnConditioner):

    def __init__(self, col, hps):
#        print(col)
        super().__init__(col, hps)
        self.converter = float

    def produce(self, data, colindex):
        super().produce(data, colindex)
        data.iloc[:,colindex] = data.iloc[:,colindex].astype(float)
        return data

    def update_metadata(self, data, ci):
        mdata = dict(data.metadata.query_column(ci).items())
        mdata['structural_type'] = float
        data.metadata = data.metadata.update_column(ci, mdata)

    def can_handle(self):
        dtype = self.data.dtype
        if dtype == float or dtype == float64:
            return self
        elif dtype == int or dtype == int64:
            return self
        else:
            return super().can_handle()


class OldTokenizedConditioner(ColumnConditioner):

    def can_handle(self):
        if any(type(x) is not str for x in self.data):
            return None
        return self

    def _calculate_median(self):
        pass

    def _construct_dict(self):
        # TODO: Allow n-grams
        # TODO: use MI with target variable to select words
        counts = {}
        for value in self.counts.keys():
            for term,freq in self._tokenize(value).items():
                try:
                    counts[term] += freq
                except KeyError:
                    counts[term] = freq
        self.keys = sorted(counts.keys(), reverse=True, key=lambda x: counts[x])
        self.dictionary = dict((self.keys[i], i+1) for i in range(len(self.keys)))

    def _tokenize(self, string):
        counts = {}
        for tok in re.findall('[a-zA-Z0-9]+', string):
            tok = tok.lower()
            try:
                counts[tok] += 1
            except KeyError:
                counts[tok] = 1
        return counts

    def produce(self, data, colindex):
        keys = self.keys
        hps = self.hps
        if hps['maximum_expansion'] > 0 and len(keys) > hps['maximum_expansion']:
            keys = keys[0:hps['maximum_expansion']]
        def convert(x):
            toks = self._tokenize(x)
            return [ toks[y] if y in toks else 0 for y in keys ]
        newcols = container.DataFrame([ convert(x) for i,x in data.iloc[:,colindex].iteritems() ],
                                      columns = ["W:" + k for k in keys])
        data = utils.append_columns(data, newcols)
        return utils.remove_columns(data, [colindex])

    def update_metadata(self, data, ci):
        pass  # Already updated


class TokenizedConditioner(ColumnConditioner):

    def can_handle(self):
        if self.hps['maximum_expansion'] < 0:
            return None
        if any(type(x) is not str for x in self.data):
            return None
        return self

    def _calculate_median(self):
        pass

    def _construct_dict(self):
        hps = self.hps
        args = {}
#        print("Tokenized width=%d" % hps['maximum_expansion'])
        if hps['maximum_expansion'] > 0:
            args['max_features'] = hps['maximum_expansion']
        self._vectr = TfidfVectorizer(**args)
        self._vectr.fit(self.data)

    def produce(self, data, colindex):
        result = self._vectr.transform(data.iloc[:,colindex])
        newcols = container.DataFrame(result.toarray(), generate_metadata=True)

        for i in range(len(newcols.columns)):
            mdata = dict(newcols.metadata.query_column(i).items())
            mdata['semantic_types'] = ('https://metadata.datadrivendiscovery.org/types/Attribute',)
            newcols.metadata = newcols.metadata.update_column(i, mdata)

        data = data.append_columns(newcols)
        return data.remove_columns([colindex])

    def update_metadata(self, data, ci):
        pass  # Already updated


class NoOpConditioner(ColumnConditioner):

    def can_handle(self):
        return self

    def fit(self):
        return self

    def produce(self, data, colindex):
        return data


class ConditionerParams(meta_params.Params):
    column_conditioners: typing.Sequence[typing.Any]
#    all_columns: typing.Sequence[typing.Any]
    width: int
    tossers: typing.Sequence[int]


class ConditionerHyperparams(meta_hyperparams.Hyperparams):
    ensure_numeric = meta_hyperparams.Hyperparameter[bool](
        default = False,
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    maximum_expansion = meta_hyperparams.Hyperparameter[int](
        default = 0,
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])


class Conditioner(pi_unsupervised.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, ConditionerParams, ConditionerHyperparams]):
    """
Perform robust type inference and imputation.  The intention is to deliver a
buck-stops-here primitive to put at the end of a data processing pipeline
and just before a pipeline that involves primitives that expect purely
numeric data with no missing values.  This primitive guarantees that the data
is safe for processing by such primitives.

It achieves this by performing type inference on each column in the input (ignoring
the assigned structural type), then assigning a type-specific conditioner to the column.
This column conditioner then transforms the data in the column to make it safe for
downstream learners.  The following types are recognized:

* **Integer**: replaces missing or ill-typed values with the column median.
* **Float**: replaces missing or ill-typed values with the column median.
* **String categorical**: Tabulates column string values.  If the number of distinct values is
  less than 20 (hard-coded currently), each distinct value is replaced with a
  distinct integer.
* **Text**: If a string column is determined not to be categorical, this
  conditioner tokenizes column contents and replaces it with one or more additional
  columns, each representing a different term, with weights set by SKLearn's TFIDFVectorizer.
  This conditioner is not selected unless all column elements are strings.
* **NoOp**: Fall-through conditioner, which is selected if none of the above conditioners
  is selected for a column

Hyperparameters:

* **ensure_numeric**:  If True, NoOp columns (typically columns of mixed type) are dropped.
* **maximum_expansion**: An integer controlling the number of additional columns generated for
  each textual column.  A positive value serves as an upper bound on the number of vocabulary
  terms to be represented, using column-wide term frequency as the ordering principle.  0 means
  full expansion (all terms). A negative value suppresses this kind of expansion; all columns
  that would have been handled by this conditioner are instead assigned to the NoOp conditioner
  (and may be dropped, depending on how ensure_numeric is set).
    """

    def __init__(self, *, hyperparams: ConditionerHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

    def get_params(self) -> ConditionerParams:
        return ConditionerParams(column_conditioners=self._column_conditioners,
#                                 all_columns=set(self._all_columns),
                                 width=self._width,
                                 tossers=self._tossers
        )

    def set_params(self, *, params: ConditionerParams) -> None:
        self._fitted = True
#        self._all_columns = params['all_columns']
        self._width = params['width']
        self._column_conditioners : typing.List[typing.Any] = params['column_conditioners']
        self._tossers = params['tossers']

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_inputs = inputs
        self._fitted = False

    def fit(self, *, timeout:float = None, iterations: int = None) -> None:
        if self._fitted:
            return

        if self._training_inputs is None:
            raise ValueError('Missing training(fitting) data.')

        data_copy = self._data_copy = self._training_inputs.copy()
#        print("Conditioner fitting a datset containing %d rows" % data_copy.shape[0])
#        self._all_columns = set(data_copy.columns)
        self._width = len(data_copy.columns)
        # self._column_conditioners = dict((c.name, self._fit_column(c)) for c in data_copy.columns)
        self._column_conditioners : typing.List[typing.Any] = []
        for i,c in enumerate(data_copy.columns):
            conditioner = self._fit_column(i)
#            print("%i, %s, %s" % (i,c,type(conditioner)))
            self._column_conditioners.append(conditioner)

        self._tossers = []
        if self.hyperparams['ensure_numeric']:
            self._tossers = [i for i in range(self._width)
                             if isinstance(self._column_conditioners[i], NoOpConditioner)]

        # print("Fitted col conditioners: %d" % len(self._column_conditioners))

        self._fitted = True
        return pi_base.CallResult(None)

    def _fit_column(self, colindex):
        col = self._data_copy.iloc[:, colindex]
#        print("Colindex: %d" % colindex)
        for cls in (IntegerConditioner, FloatConditioner, CategoricalConditioner, TokenizedConditioner, NoOpConditioner):
            obj = cls(col, self.hyperparams).can_handle()
            if obj is not None:
                obj.fit()
                # print(colname, cls)
                return obj

    def produce(self, *, inputs: Inputs, timeout:float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        if isinstance(inputs, container.DataFrame) or isinstance(inputs, pandas.DataFrame):
            data_copy = inputs.copy()
        else:
            data_copy = inputs[0].copy()

        set_columns = set(data_copy.columns)
        width = len(data_copy.columns)

#        if set_columns != self._all_columns or width != self._width:
        if width != self._width:
            raise ValueError('Columns(features) fed at produce() differ from fitted data.')

        for i in reversed(range(len(data_copy.columns))):
#        for i,col in enumerate(data_copy.columns):
            # print("Produce %d" % i)
            if i in self._tossers:
                data_copy = utils.remove_columns(data_copy, [i])
            else:
                data_copy = self._column_conditioners[i].produce(data_copy, i)
                self._column_conditioners[i].update_metadata(data_copy, i)

        return pi_base.CallResult(data_copy)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        "id": "6fdcf530-2cfe-4e87-9d9e-b8770753e19c",
        "version": config.VERSION,
        "name": "Autoflow Data Conditioner",
        "description": """
            Perform robust type inference and imputation.  The intention is to deliver a
            buck-stops-here primitive to put at the end of a data processing pipeline
            and just before a pipeline that involves primitives that expect purely
            numeric data with no missing values.  This primitive guarantees that the data
            is safe for processing by such primitives.
        """,
        "python_path": "d3m.primitives.data_transformation.conditioner.Conditioner",
        "primitive_family": meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        "algorithm_types": [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset', 'transformer' ],
        'installation': [ config.INSTALLATION ],
    })
