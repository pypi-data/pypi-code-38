from typing import List


class GroupRuleConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.module_type_list: List[str] = values.get("module_type_list", [])
        self.module_name_list: List[str] = values.get("module_name_list", [])
        self.param_name_list: List[str] = values.get("param_name_list", [])
        self.prefix_list: List[str] = values.get("prefix_list", [])
        self.kwargs: dict = values.get("kwargs", {})
        self.refuse_if_match: bool = values.get("refuse_if_match", False)
