from typing import Dict, Any


class Prediction:
    """The result obtained by taking a :class:`.Configuration` and running it through the surrogate model.

    Must contain a `mean` value.
    You cannot specify `variance` without `mean`.

    Attributes:
        json (Dict): The full Prediction object as stored in OPTaaS in JSON format.
        configuration (Dict[str, Any]): key-value pairs corresponding to the parameters and their respective values
        mean (float): Mean from surrogate model prediction
        variance (float): Variance of the surrogate model prediction. Must be >= 0.
    """

    def __init__(self, json: Dict[str, Any]) -> None:
        self.mean = json['mean']
        self.variance = json['variance']
        self.json = json
        self.configuration = json['configuration']
