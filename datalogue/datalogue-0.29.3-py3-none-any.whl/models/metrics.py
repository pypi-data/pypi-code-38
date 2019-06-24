import os
import json
import yaml
import numpy as np
from glob import glob
from typing import List, Union

from datalogue.errors import DtlError


class ArgoMetrics:
    def __init__(self, argo_work_dir: str, experiment_name: str, class_map_path: str):
        if not os.path.isdir(argo_work_dir):
            raise DtlError(
                f"{argo_work_dir} is not a directory. Path to the template's work directory(i.e. nightshade/work/cbc"
            )
        self.argo_work_dir = argo_work_dir
        self.experiment_name = experiment_name
        self.class_map = self._load_class_map(class_map_path)
        self.training_files = self._fetch_training_files()
        self.test_file = self._fetch_test_file()
        self.payload = self.create_payload()

    def _fetch_training_files(self) -> List[str]:
        tfs = sorted(glob(os.path.join(self.argo_work_dir, self.experiment_name, "control",
                                       "*-train-completed", "epoch-*-experiment-tracking.json")))
        if len(tfs) == 0:
            raise DtlError(
                f"No Training Files found in {self.argo_work_dir}, experiment: {self.experiment_name}")
        return tfs

    def _fetch_test_file(self) -> str:
        tfs = sorted(glob(os.path.join(self.argo_work_dir, self.experiment_name, "control",
                                       "*-test-completed", "test-results.json")))
        if len(tfs) == 0:
            raise DtlError(
                f"No Test Files found in {self.argo_work_dir}, experiment: {self.experiment_name}")
        return tfs[-1]

    @staticmethod
    def _load_class_map(class_map_path: str) -> dict:
        if not os.path.isfile(class_map_path):
            raise DtlError(
                f"{class_map_path} is not a file. Please provide a Json or Yaml file!"
            )
        with open(class_map_path, 'r', encoding='utf-8') as f:
            if class_map_path.endswith('json'):
                return json.load(f)
            elif class_map_path.endswith('yaml'):
                return yaml.load(f)
            raise DtlError(
                f"{class_map_path} is not Json or Yaml. Unable to Load Class Map")

    def get_metrics(self, conf_mat: List[List], phase_name: str, class_names: List[str]) -> dict:
        rev_class_map = {v: k for k, v in self.class_map.items()}
        fp = conf_mat.sum(axis=0) - np.diag(conf_mat)
        fn = conf_mat.sum(axis=1) - np.diag(conf_mat)
        tp = np.diag(conf_mat)
        tn = conf_mat.sum() - (fp + fn + tp)
        epsilon = 1e-15  # So that we cannot get division by 0 errors
        # Sensitivity, hit rate, recall, or true positive rate
        tpr = tp / (tp + fn + epsilon)
        fpr = fp / (fp + tn + epsilon)
        recall = {rev_class_map[i]: float(tpr[i]) for i in range(len(tpr))}
        # Precision or positive predictive value
        ppv = tp / (tp + fp + epsilon)
        precision = {rev_class_map[i]: float(ppv[i]) for i in range(len(ppv))}
        # f1 Score
        f1 = 2 * tpr * ppv / (tpr + ppv + epsilon)
        f1_score = {rev_class_map[i]: float(f1[i]) for i in range(len(f1))}

        evaluation = {'f1': f1_score,
                      'recall': recall,
                      'precision': precision,
                      'fpr': np.mean(fpr),
                      'tpr': np.mean(tpr)
                      }

        return evaluation

    def create_payload(self) -> List[dict]:
        payload = []
        for file in self.training_files:
            with open(file, 'r') as f:
                data = json.load(f)
            M = {"epoch": data["epoch"], 'metrics': {}}
            for phase in ["training", "validation"]:
                M['metrics'][phase] = {
                    "loss": data["metrics"][phase]["loss"],
                    "acc": data["metrics"][phase]["acc"],
                    "avg_precision_loss": data["metrics"][phase]["avg_precision_loss"],
                    "precision":  data["metrics"][phase]["precision"],
                    "recall":  data["metrics"][phase]["recall"],
                    "f1": data["metrics"][phase]["f1"],
                    "tpr": data["metrics"][phase]["tpr"] if "tpr" in data["metrics"][phase] else None,
                    "fpr": data["metrics"][phase]["fpr"] if "fpr" in data["metrics"][phase] else None,
                    "confusion_matrix": None if "training" == phase else data["metrics"][phase]["confusion_matrix"]
                }
                if "validation" == phase:
                    conf_mat = np.array(
                        data["metrics"][phase]["confusion_matrix"]["matrix"])
                    evaluation = self.get_metrics(
                        conf_mat, phase_name=f"{self.experiment_name}_VAL_epoch_{data['epoch']}_", class_names=data["metrics"][phase]["confusion_matrix"]["index"])
                    M['metrics'][phase].update(evaluation)
            payload.append(M)

        with open(self.test_file, 'r') as f:
            test_data = json.load(f)

        M = {"epoch": len(self.training_files), 'metrics': {}}
        for phase in ["training", "validation"]:
            M['metrics'][phase] = {
                "loss": test_data["metrics"]["test"]["loss"],
                "acc": test_data["metrics"]["test"]["acc"],
                "avg_precision_loss": test_data["metrics"]["test"]["avg_precision_loss"],
                "precision": test_data["metrics"]["test"]["precision"],
                "recall": test_data["metrics"]["test"]["recall"],
                "f1": test_data["metrics"]["test"]["f1"],
                "confusion_matrix": test_data["metrics"]["test"]["confusion_matrix"]
            }

            conf_mat = np.array(test_data["metrics"]["test"]
                                ["confusion_matrix"]["matrix"])
            evaluation = self.get_metrics(conf_mat,
                                          phase_name=f"{self.experiment_name}_test_",
                                          class_names=test_data["metrics"]["test"]["confusion_matrix"]["index"])
            M['metrics'][phase].update(evaluation)
        payload.append(M)
        return payload
