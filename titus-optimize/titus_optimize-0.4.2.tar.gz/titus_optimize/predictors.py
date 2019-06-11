import json
from base64 import b64decode, b64encode
import pickle
from datetime import datetime as dt

import lightgbm as lgb

class PredictorWithFilter(object):
    
    def __init__(self, ml_model, filter_, meta={}):
        self.ml_model = ml_model
        self.filter = filter_
        self.meta_data = meta.copy()
    
    
    def serialize(self):
        return b64encode(json.dumps({
            "version": "v2.0",
            "created_at": dt.utcnow().isoformat(),
            "ml_model": self.ml_model.serialize(),
            "filter" : json.dumps(list(self.filter)),
            "meta_data" : json.dumps(self.meta_data)
        }).encode())
    
    
    @staticmethod
    def load(blob):
        payload = json.loads(b64decode(blob).decode())
        if payload["version"] not in ("v1.0", "v2.0"):
            raise Exception("Unknown model version `%s`" % (payload["version"]))
        ml_model = Predictor.load(payload["ml_model"])
        digest_filter = set(json.loads(payload["filter"]))
        meta_data = json.loads(payload["meta_data"])
        return PredictorWithFilter(ml_model, digest_filter, meta_data)

class Predictor(object):

    def __init__(self, **lgb_params):
        self.lgb_params = lgb_params.copy() if lgb_params is not None else {}
        self.model = None
        self.encoder = None
        self.cat_feats = 'auto'
        self.min_prediction = 0.01
        
    def set_encoder(self, encoder):
        self.encoder = encoder
        cf_names = set(encoder.column_names['categorical'])-set(encoder.column_names['dense_bow'])
        if len(cf_names) > 0:
            self.cat_feats = sorted([encoder.lookup_index[name][0] for name in cf_names])

    def predict(self, X, ntrees=0):
        return self.model.predict(X, num_iteration=ntrees)
    
    def predict_single(self, query):
        x = self.encoder.transform_single(query)
        return max(self.model.predict(x)[0], self.min_prediction)
    
    def serialize(self):
        return {
            "version": "v2.0",
            "created_at": dt.utcnow().isoformat(),
            "params": self.lgb_params,
            "model": self.model.model_to_string(),
            "encoder": b64encode(pickle.dumps(self.encoder)).decode()
        }
    
    @staticmethod
    def load(payload):
        if payload["version"] not in ("v1.0", "v2.0"):
            raise Exception("Unknown model version `%s`" % (payload["version"]))
        model = Predictor()
        model.lgb_params = payload["params"].copy()
        model.model = lgb.Booster(dict(list(model.lgb_params.items()) + [("model_str", payload["model"])]))
        model.set_encoder(pickle.loads(b64decode(bytes(payload["encoder"], "utf-8"))))
        return model