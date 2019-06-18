from tcell_agent.policies.base_policy import TCellPolicy


class LoginPolicy(TCellPolicy):
    api_identifier = "login"

    def __init__(self, native_agent, enablements, _):
        super(LoginPolicy, self).__init__()
        self.native_agent = native_agent
        self.login_success_enabled = False
        self.login_failed_enabled = False

        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.login_success_enabled = enablements.get("login_success_enabled", False)
        self.login_failed_enabled = enablements.get("login_failed_enabled", False)

    def report_login_success(self,
                             user_id,
                             header_keys,
                             tcell_context):
        return self.native_agent.login_fraud_apply(
            success=True,
            user_id=user_id,
            password=None,
            header_keys=header_keys,
            user_valid=True,
            tcell_context=tcell_context
        )

    def report_login_failure(self,
                             user_id,
                             password,
                             header_keys,
                             user_valid,
                             tcell_context):
        return self.native_agent.login_fraud_apply(
            success=False,
            user_id=user_id,
            password=password,
            header_keys=header_keys,
            user_valid=user_valid,
            tcell_context=tcell_context
        )
