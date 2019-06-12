import xgboost as xgb
from typing import Dict, List
from pandas import DataFrame
from .gridsearcher import GridSearcher
from .recorder import Recorder
from .partition import Partition


class Tuner(Recorder):
    def __init__(self):
        super().__init__()
        pass
    
    def tune(
        self, 
        model_type: str,
        search_params: Dict,
        set_params: Dict, 
        dataset: DataFrame ,
        features: List[str],
        targets: List[str],
        folds: int,
        search_type = GridSearcher,
    ) -> List[Dict]:
        if (len(search_params) == 0):
            raise ValueError("No search parameters provided")

        self.param_searcher = search_type(search_params)
        self.set_params = set_params
        self.dataset = dataset
        self.folds = folds
        self.features = features
        self.targets = targets
        self.model_type = model_type
        self.records = []

        return self.tune_classifier()

    def tune_classifier(self) -> List[Dict]:
        for candidates in self.param_searcher:
            # Candidates will override conflicting self.set_params
            args: Dict = {**self.set_params, **candidates}
            self.records.append(self.score_parameters(args))
        
        self.average_scores(self.folds)
        self.sort_records()
        return self.records

    def score_parameters(self, params: Dict):
        folds = Partition(self.dataset, self.folds)
        cl = self.new_model(params)
        record = {
            "test_score": 0,
            "train_score": 0,
            "params": params
        }
        for fold in folds:
            train_features = fold["train"][self.features]
            train_targets = fold["train"][self.targets]
            test_features = fold["test"][self.features]
            test_targets = fold["test"][self.targets]
            cl.fit(train_features, train_targets.values.ravel())
            record["train_score"] += cl.score(train_features, train_targets)
            record["test_score"] += cl.score(test_features, test_targets)
        
        return record

    def new_model(self, params:Dict):
        if self.model_type == "classifier":
            return xgb.XGBClassifier(**params)
        elif self.model_type == "regressor":
            return xgb.XGBRegressor(**params)
        else:
            raise(ValueError("unexpected model_type: %s" % self.model_type))
    
    def tune_and_sort(self) -> List[Dict]:
        self.tune_classifier()
        self.sort_records()
        return self.records
        
    def save_score(self, params_used: Dict, train_score: float, test_score: float):
        self.records.append({
            "test_score": test_score,
            "train_score": train_score,
            "params": params_used
        })