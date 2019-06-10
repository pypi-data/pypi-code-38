class Validator:
    def __init__(self, rules_dict: dict):
        """

        :param rules_dict: { field: [rule_functions] }
        """
        self.rules = rules_dict

    def validate(self, dict_to_check: dict, stop_on_exception=False):
        errors = {}
        results = True
        for field in self.rules:
            check_functions = self.rules.get(field)
            if not isinstance(check_functions, list):
                check_functions = [check_functions]

            result, err_messages = Validator._validate_field(field, check_functions, dict_to_check)

            if len(err_messages):
                errors[field] = err_messages
            results = result and results

            if not results and stop_on_exception:
                break

        return results, errors

    @staticmethod
    def _validate_field(field, functions_to_check, dict_to_check):
        errors = []
        results = True
        for check_fn in functions_to_check:
            res, err_message = check_fn(field, dict_to_check)
            results = results and res
            if err_message:
                errors.append(err_message)
        return results, errors
