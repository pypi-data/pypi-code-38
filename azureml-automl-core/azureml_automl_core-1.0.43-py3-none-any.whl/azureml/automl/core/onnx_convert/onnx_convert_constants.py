# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used by the AutoML ONNX convert."""


class OnnxConvertConstants:
    """Names for all model/operator names and ONNX operator names."""

    # The python version that is incompatible with onnx.
    OnnxIncompatiblePythonVersion = (3, 7)

    OnnxModelProducer = 'AutoML'

    # Telemetry tags.
    LoggingTagPrefix = '[ONNXConverter]'
    EvtInitInput = '[InitInput]'
    EvtConvert = '[Convert]'

    StatusStart = '[Start]'
    StatusWarning = '[Warning]'
    StatusError = '[Error]'
    StatusEndSucceeded = '[End.Succeeded]'
    StatusEndFailed = '[End.Failed]'

    # Onnx model resources.
    InputRawColumnSchema = 'InputRawColumnSchema'
    InputOnnxColumnSchema = 'InputOnnxColumnSchema'
    RawColumnNameToOnnxNameMap = 'RawColumnNameToOnnxNameMap'

    # Other data type names in the raw input data.
    Boolean = 'boolean'
    Mixed = 'mixed'

    # ---------------------------
    # Onnx domain names.
    # The traditional ML domain.
    OnnxMLDomain = 'ai.onnx.ml'
    # The MS domain.
    OnnxMSDomain = 'com.microsoft'

    # ---------------------------
    # The onnx op set version the whole converter is using.
    CurrentOnnxOPSetVersion = 10

    # ---------------------------
    # ONNX Operator names.
    ArrayFeatureExtractor = 'ArrayFeatureExtractor'
    FeatureVectorizer = 'FeatureVectorizer'
    OneHotEncoder = 'OneHotEncoder'
    LabelEncoder = 'LabelEncoder'
    Scaler = 'Scaler'

    IsNaN = 'IsNaN'
    Equal = 'Equal'
    And = 'And'
    Or = 'Or'
    Less = 'Less'
    Where = 'Where'

    MurmurHash3 = 'MurmurHash3'
    Cast = 'Cast'

    Tokenizer = 'Tokenizer'

    Sum = 'Sum'
    Sub = 'Sub'
    Div = 'Div'
    Mul = 'Mul'

    Slice = 'Slice'
    Concat = 'Concat'
    ReduceMax = 'ReduceMax'
    ReduceMean = 'ReduceMean'
    ArgMax = 'ArgMax'

    # ---------------------------
    # Dependent pkg Model/Operator names.
    SklearnCountVectorizer = 'SklearnCountVectorizer'
    LightGbmLGBMClassifier = 'LightGbmLGBMClassifier'
    LightGbmLGBMRegressor = 'LightGbmLGBMRegressor'
    XGBClassifier = 'XGBClassifier'
    XGBRegressor = 'XGBRegressor'
