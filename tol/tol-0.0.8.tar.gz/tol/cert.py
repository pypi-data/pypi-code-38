def domain_to_star_cert_filename(domain):
    return "_".join(["star"] + domain.split("."))


def create_csr_command(domain, country_code, state, locality, organization):
    """
    Helper to create command for creating csr
    
    Instructions are here:
        https://www.digicert.com/easy-csr/openssl.htm
    """
    filename = domain_to_star_cert_filename(domain)
    
    cmd = 'openssl req -new -newkey rsa:2048 -nodes'
    cmd += ' -out %s.csr -keyout %s.key' % ((filename,) * 2)
    cmd += ' -subj "/C=%s/ST=%s/L=%s/O=%s/CN=*.%s"' % (
        country_code,
        state,
        locality,
        organization,
        domain
    )
    return cmd


def create_self_sign_csr_command(domain):
    """
    Helper to create command to self-sign csr
    """
    filename = domain_to_star_cert_filename(domain)
    cmd = 'openssl x509 -req -days 365'
    cmd += ' -in %s.csr -signkey %s.key -out %s.crt' % ((filename,) * 3)
    return cmd
