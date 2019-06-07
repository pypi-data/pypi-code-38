# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import os
import json


def joblib_save_model_to_dir(model, path):
    filename = path[path.rfind(os.path.sep)+1:] + '.pkl'
    os.makedirs(path)
    from sklearn.externals import joblib
    joblib.dump(model, os.path.join(path, filename))


def create_scikit_learn_model_data(model_name='digits'):
    from sklearn import datasets
    from sklearn.pipeline import Pipeline
    from sklearn import preprocessing
    from sklearn import decomposition
    from sklearn import svm

    global model_data
    global model

    if model_name == 'digits':
        model_data = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])
    if model_name == 'iris':
        model_data = datasets.load_iris()
        pca = decomposition.PCA()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('pca', pca), ('svc', clf)])
        model = pipeline.fit(model_data.data, model_data.target)
        predicted = model.predict(model_data.data[1: 10])

    return {
        'model': model,
        'pipeline': pipeline,
        'training_data': model_data.data,
        'training_target': model_data.target,
        'prediction': predicted
    }


def create_scikit_learn_model_directory(path):
    model_data = create_scikit_learn_model_data()
    joblib_save_model_to_dir(model_data['model'], path)


def create_scikit_learn_xgboost_model_data():
    from xgboost.sklearn import XGBClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.datasets import load_svmlight_file

    (X, y_train) = load_svmlight_file(os.path.join('artifacts', 'agaricus.txt.train'))
    X_train = X.toarray()
    param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
    # num_round = 2

    global model
    model = Pipeline([('scaler', StandardScaler()), ('classifier', XGBClassifier())])
    model.fit(X_train, y_train)
    predicted = model.predict(X_train[0:5, :])

    return {
        'model': model,
        'prediction': predicted
    }


def create_scikit_learn_xgboost_model_directory(path):
    model_data = create_scikit_learn_xgboost_model_data()
    joblib_save_model_to_dir(model_data['model'], path)


def create_spark_mllib_model_data():
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import StringIndexer, IndexToString, VectorAssembler
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml import Pipeline

    spark = SparkSession.builder.getOrCreate()

    # df = spark.read.load(
    #     os.path.join(os.environ['SPARK_HOME'], 'data', 'mllib', 'sample_binary_classification_data.txt'),
    #     format='libsvm')

    df_data = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option('inferSchema', 'true') \
        .load("datasets/GoSales/GoSales_Tx_NaiveBayes.csv")

    splitted_data = df_data.randomSplit([0.8, 0.18, 0.02], 24)
    train_data = splitted_data[0]
    test_data = splitted_data[1]
    predict_data = splitted_data[2]

    stringIndexer_label = StringIndexer(inputCol="PRODUCT_LINE", outputCol="label").fit(df_data)
    stringIndexer_prof = StringIndexer(inputCol="PROFESSION", outputCol="PROFESSION_IX")
    stringIndexer_gend = StringIndexer(inputCol="GENDER", outputCol="GENDER_IX")
    stringIndexer_mar = StringIndexer(inputCol="MARITAL_STATUS", outputCol="MARITAL_STATUS_IX")

    vectorAssembler_features = VectorAssembler(inputCols=["GENDER_IX", "AGE", "MARITAL_STATUS_IX", "PROFESSION_IX"],
                                               outputCol="features")
    rf = RandomForestClassifier(labelCol="label", featuresCol="features")
    labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                   labels=stringIndexer_label.labels)
    pipeline_rf = Pipeline(stages=[stringIndexer_label, stringIndexer_prof, stringIndexer_gend, stringIndexer_mar,
                                   vectorAssembler_features, rf, labelConverter])
    model_rf = pipeline_rf.fit(train_data)

    return {
        'model': model_rf,
        'pipeline': pipeline_rf,
        'training_data': train_data,
        'test_data': test_data,
        'prediction': predict_data,
        'labels': stringIndexer_label.labels,
        #'output_schema': ''
    }


def create_best_drug_spark_model():
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import StringIndexer, IndexToString, VectorAssembler
    from pyspark.ml.classification import RandomForestClassifier
    from pyspark.ml import Pipeline
    from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType

    spark = SparkSession.builder.getOrCreate()

    df_data = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option("delimiter", ';') \
        .option('inferSchema', 'true') \
        .load("datasets/drugs/drug_feedback_data.csv")

    df_test = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option("delimiter", ';') \
        .option('inferSchema', 'true') \
        .load("datasets/drugs/drug_feedback_test.csv")

    stringIndexer_label = StringIndexer(inputCol="DRUG", outputCol="label").fit(df_data)
    stringIndexer_sex = StringIndexer(inputCol="SEX", outputCol="SEX_IX")
    stringIndexer_bp = StringIndexer(inputCol="BP", outputCol="BP_IX")
    stringIndexer_chol = StringIndexer(inputCol="CHOLESTEROL", outputCol="CHOLESTEROL_IX")

    vectorAssembler_features = VectorAssembler(inputCols=["AGE", "SEX_IX", "BP_IX", "CHOLESTEROL_IX", "NA", "K"],
                                               outputCol="features")
    rf = RandomForestClassifier(labelCol="label", featuresCol="features")
    labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                                   labels=stringIndexer_label.labels)
    pipeline_rf = Pipeline(stages=[stringIndexer_label, stringIndexer_sex, stringIndexer_bp, stringIndexer_chol,
                                   vectorAssembler_features, rf, labelConverter])
    model_rf = pipeline_rf.fit(df_data)

    train_data_schema = df_data.schema
    label_field = next(f for f in train_data_schema.fields if f.name == "DRUG")
    label_field.metadata['values'] = stringIndexer_label.labels

    input_fileds = filter(lambda f: f.name != "DRUG", train_data_schema.fields)

    output_data_schema = StructType(list(input_fileds)). \
        add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
        add("predictedLabel", StringType(), True,
            {'modeling_role': 'decoded-target', 'values': stringIndexer_label.labels}). \
        add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

    return {
        'model': model_rf,
        'pipeline': pipeline_rf,
        'training_data': df_data,
        'test_data': df_test,
        'prediction': df_test,
        'labels': stringIndexer_label.labels,
        'output_schema': output_data_schema.jsonValue()
    }


def create_spark_mllib_regression_model(path):
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import RFormula
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml import Pipeline

    spark = SparkSession.builder.getOrCreate()

    df_data = spark.read \
        .format('org.apache.spark.sql.execution.datasources.csv.CSVFileFormat') \
        .option('header', 'true') \
        .option('inferSchema', 'true') \
        .option('nanValue', ' ') \
        .option('nullValue', ' ') \
        .load(path)

    df_complete = df_data.dropna()
    df_complete.drop('Churn')

    (train_data, test_data) = df_complete.randomSplit([0.8, 0.2], 24)

    features = RFormula(
        formula="~ gender + SeniorCitizen +  Partner + Dependents + tenure + PhoneService + MultipleLines + "
                "InternetService + OnlineSecurity + OnlineBackup + DeviceProtection + TechSupport + StreamingTV + "
                "StreamingMovies + Contract + PaperlessBilling + PaymentMethod + MonthlyCharges - 1")

    lr = LinearRegression(labelCol='TotalCharges')
    pipeline_lr = Pipeline(stages=[features, lr])
    lr_model = pipeline_lr.fit(train_data)
    lr_predictions = lr_model.transform(test_data)

    return {
        'model': lr_model,
        'pipeline': pipeline_lr,
        'training_data': train_data,
        'test_data': test_data,
        'prediction': lr_predictions
    }


def create_spark_mllib_model_directory(path):
    model_data = create_spark_mllib_model_data()
    model_data['model'].write.overwrite.save(path)


def create_keras_model_score():
    data_fn = os.path.join('datasets', 'cars4u', 'car_rental_score_data.json')
    with open(data_fn) as f_json:
        score_data = json.load(f_json)
    return {'model_path': os.path.join('artifacts', 'keras_cars4u', 'keras_satisfaction_model.tar.gz'),
            'scoring_payload': score_data}


def create_xgboost_model_data():
    import xgboost as xgb
    global agaricus
    agaricus = xgb.DMatrix(os.path.join('artifacts', 'agaricus.txt.train'))
    param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
    num_round = 2

    global model
    model = xgb.train(params=param, dtrain=agaricus, num_boost_round=num_round)
    predicted = model.predict(agaricus.slice(range(5)))

    return {
        'model': model,
        'params': param,
        'prediction': predicted
    }


def create_xgboost_model_directory(path):
    model_data = create_xgboost_model_data()
    joblib_save_model_to_dir(model_data['model'], path)