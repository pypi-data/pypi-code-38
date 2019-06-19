from typing import Dict, List

class Recorder():
    def __init__(self):
        self.records = []
    
    def sort_records(self):
        self.records = sorted(self.records, key = lambda i: i["test_score"], reverse=True)
    
    def best_n_params(self, records_wanted: int) -> List[Dict]:
        self.pre_process()
        return self.records[:records_wanted]

    def best_params(self) -> Dict:
        self.pre_process()
        return self.records[0]
    
    def pre_process(self):
        self.confirm_records()
        self.sort_records()

    def aggeregate(self, new_records: List[Dict]) -> None:
        if (len(new_records) != len(self.records)):
            raise ValueError("Records to be aggregated are not the same length as current records")
        for index, record in enumerate(new_records):
            current_record = self.records[index]

            for key, value in current_record["params"].items():
                assert(value == record["params"][key])

            current_record["test_score"] += record["test_score"]
            current_record["train_score"] += record["train_score"]

    def average_scores(self, folds: int) -> None:
        for record in self.records:
            record["test_score"] /= folds
            record["train_score"] /= folds

    def confirm_records(self):
        if (len(self.records) == 0):
            raise RuntimeError("Attempt to access tuning results before tuning has occurred")