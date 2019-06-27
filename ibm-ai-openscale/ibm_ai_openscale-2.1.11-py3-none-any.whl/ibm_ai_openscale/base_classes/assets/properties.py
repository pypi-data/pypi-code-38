# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

class Properties:
    """
    For configuration, describes possible asset properties.

    """

    # TODO - add enums and make return list dynamic

    @staticmethod
    def get_properties_names():
        return ["model_type", "runtime_environment", "training_data_reference", "training_data_schema",
                "input_data_schema", "output_data_schema", "label_column", "input_data_type",
                "predicted_target_field", "prediction_probability_field"]
