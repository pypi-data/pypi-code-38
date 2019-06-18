from tcell_agent.config.configuration import get_config


def better_ip_address(request_env):
    if not get_config().reverse_proxy:
        return request_env.get("REMOTE_ADDR", "1.1.1.1")
    else:
        try:
            reverse_proxy_header = get_config().reverse_proxy_ip_address_header
            if reverse_proxy_header is None:
                reverse_proxy_header = "HTTP_X_FORWARDED_FOR"
            else:
                reverse_proxy_header = "HTTP_" + reverse_proxy_header.upper().replace("-", "_")
            x_forwarded_for = request_env.get(reverse_proxy_header, request_env.get("REMOTE_ADDR", "1.1.1.1"))
            if x_forwarded_for and x_forwarded_for != "":
                ip = x_forwarded_for.split(",")[0].strip()
            else:
                ip = request_env.get("REMOTE_ADDR", "1.1.1.1")
            return ip
        except Exception:
            return request_env.get("REMOTE_ADDR", "1.1.1.1")


def tcell_get_host(request):
    """Returns the HTTP host using the environment or request headers."""
    from django.conf import settings as d_settings
    if d_settings.USE_X_FORWARDED_HOST and (
            'HTTP_X_FORWARDED_HOST' in request.META):
        host = request.META['HTTP_X_FORWARDED_HOST']
    elif 'HTTP_HOST' in request.META:
        host = request.META['HTTP_HOST']
    else:
        # Reconstruct the host using the algorithm from PEP 333.
        host = request.META['SERVER_NAME']
        server_port = str(request.META['SERVER_PORT'])
        if server_port != ('443' if request.is_secure() else '80'):
            host = host + ':' + server_port
    return host
