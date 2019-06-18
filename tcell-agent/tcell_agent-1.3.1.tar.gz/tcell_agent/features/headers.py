from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes


def add_headers(headers, tcell_context):
    headers_policy = TCellAgent.get_policy(PolicyTypes.HEADERS)
    tcell_headers = headers_policy.get_headers(tcell_context)
    for header_info in tcell_headers:
        header_name = header_info["name"]
        header_value = header_info["value"]
        existing_header_value = headers.get(header_name)
        if existing_header_value:
            headers[header_name] = "{}, {}".format(existing_header_value, header_value)
        else:
            headers[header_name] = header_value
