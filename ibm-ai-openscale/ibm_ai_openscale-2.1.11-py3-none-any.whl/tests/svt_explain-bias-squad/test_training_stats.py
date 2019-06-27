# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import pandas as pd
import unittest
import json

from ibm_ai_openscale.supporting_classes.enums import ProblemType
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.utils.training_stats import TrainingStats



class TestAIOpenScaleClient(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
        
    def test_distribution_1(self):
        file = './datasets/German_credit_risk/credit_risk_training.csv'
        data_df = pd.read_csv(
            file,
            dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
                   'Age': int, 'ExistingCreditsCount': int, 'Dependents': int}
        )
        input = {
                "problem_type": ProblemType.BINARY_CLASSIFICATION,
                "label_column": 'Risk',
                "feature_columns": ['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                                    'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex',
                                    'OthersOnLoan', 'CurrentResidenceDuration', 'OwnsProperty', 'Age',
                                    'InstallmentPlans', 'Housing', 'ExistingCreditsCount', 'Job', 'Dependents',
                                    'Telephone', 'ForeignWorker'],
                "categorical_columns": ['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                        'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty',
                                        'InstallmentPlans', 'Housing', 'Job', 'Telephone', 'ForeignWorker'],
                "fairness_inputs": {
                    "fairness_attributes": [
                        {
                            "majority": [[26, 75]],
                            "minority": [[18, 25]],
                            "type": "int",
                            "feature": "Age",
                            "threshold": 0.95
                        },
                        {
                            "majority": ["male"],
                            "minority": ["female"],
                            "type": "string",
                            "feature": "Sex",
                            "threshold": 0.95
                        }
                    ],
                    "min_records": 4,
                    "favourable_class": ['No Risk'],
                    "unfavourable_class": ['Risk']

                }
            }
        TestAIOpenScaleClient.training_data_statistics = TrainingStats(
            data_df, input
        ).get_training_statistics()
        
        row_count,col_count = data_df.shape
        
        #stats = json.dumps(TestAIOpenScaleClient.training_data_statistics,indent=2)
        stats = TestAIOpenScaleClient.training_data_statistics
        assert stats is not None
        assert 'common_configuration' in stats
        assert 'explainability_configuration' in stats
        assert 'fairness_configuration' in stats
        
        
        common_config = stats['common_configuration']
        assert common_config['label_column'] == input['label_column']
        assert common_config['problem_type'] == input['problem_type']
        assert 'input_data_schema' in common_config
        assert common_config['feature_fields'] == input['feature_columns']
        assert common_config['categorical_fields'] == input['categorical_columns']
        
        assert 'parameters' in stats['fairness_configuration']
        assert "features" in stats['fairness_configuration']['parameters']
        
        features = stats['fairness_configuration']['parameters']['features']
        for fea in features:
            assert "feature" in fea
            assert "minority" in fea
            assert "majority" in fea
            assert "threshold" in fea
         
        assert "distributions" in stats['fairness_configuration']
        distributions = stats['fairness_configuration']['distributions']
        label_column = None
        attribute_list = []
        for att in distributions:
            count = 0
            name = att["attribute"]
            if 'is_class_label'  in att:
                label_column = name
            else:
                attribute_list.append(name)
                class_labels = att['class_labels']  
                assert len(class_labels) <= 55 
                for cl in class_labels:
                    counts = cl['counts'] 
                    for cnt in counts:
                        count+=cnt['count']
                        
                assert count == row_count        
        assert label_column == input['label_column'] 
        assert 'Age' in attribute_list
        assert 'Sex' in attribute_list
        
        explainability = stats['explainability_configuration']
        
        assert 'feature_columns' in explainability
        assert 'categorical_columns' in explainability
        assert 'feature_values' in explainability
        assert 'feature_frequencies' in explainability
        assert 'class_labels' in explainability
        assert 'categorical_columns_encoding_mapping' in explainability
        assert 'd_means' in explainability
        assert 'd_stds' in explainability
        assert 'd_maxs' in explainability
        assert 'd_mins' in explainability
        assert 'd_bins' in explainability
        assert 'base_values' in explainability
        assert 'stds' in explainability
        assert 'mins' in explainability
        assert 'maxs' in explainability
        assert 'categorical_counts' in explainability
        
        
        
        
        