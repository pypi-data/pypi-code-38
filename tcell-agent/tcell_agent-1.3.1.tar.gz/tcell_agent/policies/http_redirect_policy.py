from tcell_agent.policies.base_policy import TCellPolicy


class HttpRedirectPolicy(TCellPolicy):
    api_identifier = "http-redirect"

    def __init__(self, native_agent, enablements, _):
        super(HttpRedirectPolicy, self).__init__()
        self.native_agent = native_agent
        self.enabled = False
        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.enabled = enablements.get("http_redirect", False)

    def process_location(self,
                         redirect_url,
                         from_domain,
                         status_code,
                         tcell_context):
        if not self.enabled:
            return redirect_url

        redirect_response = self.native_agent.check_http_redirect(
            redirect_url,
            from_domain,
            status_code,
            tcell_context)

        if redirect_response.get("block", False):
            return "/"

        return redirect_url
